import uuid

from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import OptimizationTask, PerformanceMetric, Route, Schedule, Train
from .optimization import PerformanceAnalyzer
from .serializers import (DashboardMetricsSerializer,
                          OptimizationTaskCreateSerializer,
                          OptimizationTaskSerializer,
                          PerformanceMetricCreateSerializer,
                          PerformanceMetricSerializer, RouteSerializer,
                          ScheduleCreateSerializer, ScheduleSerializer,
                          TrainSerializer)
from .tasks import run_optimization_task


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class RouteViewSet(viewsets.ModelViewSet):
    """ViewSet for Route model"""

    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active", "start_station", "end_station"]
    search_fields = ["name", "start_station", "end_station"]
    ordering_fields = ["name", "distance", "created_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["get"])
    def performance(self, request, pk=None):
        """Get performance metrics for a specific route"""
        route = self.get_object()
        days = int(request.query_params.get("days", 30))

        performance_data = PerformanceAnalyzer.analyze_route_performance(route.id, days)
        return Response(performance_data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get only active routes"""
        active_routes = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_routes, many=True)
        return Response(serializer.data)


class TrainViewSet(viewsets.ModelViewSet):
    """ViewSet for Train model"""

    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["train_type", "is_operational"]
    search_fields = ["train_id", "train_type"]
    ordering_fields = [
        "train_id",
        "capacity",
        "max_speed",
        "fuel_efficiency",
        "created_at",
    ]
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"])
    def operational(self, request):
        """Get only operational trains"""
        operational_trains = self.queryset.filter(is_operational=True)
        serializer = self.get_serializer(operational_trains, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def schedules(self, request, pk=None):
        """Get schedules for a specific train"""
        train = self.get_object()
        schedules = Schedule.objects.filter(train=train).order_by("-departure_time")

        # Apply date filtering if provided
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if date_from:
            schedules = schedules.filter(departure_time__gte=date_from)
        if date_to:
            schedules = schedules.filter(departure_time__lte=date_to)

        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for Schedule model"""

    queryset = Schedule.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["train", "route", "is_cancelled"]
    search_fields = ["train__train_id", "route__name"]
    ordering_fields = ["departure_time", "arrival_time", "created_at"]
    ordering = ["-departure_time"]

    def get_serializer_class(self):
        if self.action == "create":
            return ScheduleCreateSerializer
        return ScheduleSerializer

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Get today's schedules"""
        today = timezone.now().date()
        today_schedules = self.queryset.filter(
            departure_time__date=today, is_cancelled=False
        ).order_by("departure_time")

        serializer = self.get_serializer(today_schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get upcoming schedules"""
        now = timezone.now()
        upcoming_schedules = self.queryset.filter(
            departure_time__gte=now, is_cancelled=False
        ).order_by("departure_time")[:10]

        serializer = self.get_serializer(upcoming_schedules, many=True)
        return Response(serializer.data)


class OptimizationTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for OptimizationTask model"""

    queryset = OptimizationTask.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "optimization_type", "user"]
    search_fields = ["task_id", "optimization_type"]
    ordering_fields = ["created_at", "start_time", "end_time"]
    ordering = ["-created_at"]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return OptimizationTaskCreateSerializer
        return OptimizationTaskSerializer

    def perform_create(self, serializer):
        """Create optimization task and start background processing"""
        task_id = str(uuid.uuid4())
        task = serializer.save(
            user=self.request.user, task_id=task_id, status="pending"
        )

        # Start background optimization task
        run_optimization_task.delay(
            task_id=task.task_id,
            optimization_type=task.optimization_type,
            parameters=task.parameters,
        )

    @action(detail=True, methods=["post"])
    def restart(self, request, pk=None):
        """Restart a failed optimization task"""
        task = self.get_object()

        if task.status != "failed":
            return Response(
                {"error": "Only failed tasks can be restarted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reset task status
        task.status = "pending"
        task.start_time = None
        task.end_time = None
        task.error_message = ""
        task.results = {}
        task.save()

        # Restart background task
        run_optimization_task.delay(
            task_id=task.task_id,
            optimization_type=task.optimization_type,
            parameters=task.parameters,
        )

        return Response({"message": "Task restarted successfully"})

    @action(detail=False, methods=["get"])
    def my_tasks(self, request):
        """Get tasks for the current user"""
        user_tasks = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(user_tasks, many=True)
        return Response(serializer.data)


class PerformanceMetricViewSet(viewsets.ModelViewSet):
    """ViewSet for PerformanceMetric model"""

    queryset = PerformanceMetric.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["metric_type", "train", "route"]
    search_fields = ["metric_type", "unit"]
    ordering_fields = ["measured_at", "value", "created_at"]
    ordering = ["-measured_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return PerformanceMetricCreateSerializer
        return PerformanceMetricSerializer

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Get dashboard metrics"""
        metrics = PerformanceAnalyzer.generate_dashboard_metrics()
        serializer = DashboardMetricsSerializer(data=metrics)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def trends(self, request):
        """Get performance trends over time"""
        metric_type = request.query_params.get("type", "fuel_consumption")
        days = int(request.query_params.get("days", 30))

        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=days)

        metrics = self.queryset.filter(
            metric_type=metric_type,
            measured_at__gte=start_date,
            measured_at__lte=end_date,
        ).order_by("measured_at")

        # Group by date and calculate daily averages
        daily_metrics = {}
        for metric in metrics:
            date_key = metric.measured_at.date()
            if date_key not in daily_metrics:
                daily_metrics[date_key] = []
            daily_metrics[date_key].append(metric.value)

        # Calculate averages
        trend_data = []
        for date, values in daily_metrics.items():
            trend_data.append(
                {
                    "date": date,
                    "average_value": sum(values) / len(values),
                    "count": len(values),
                }
            )

        return Response(
            {
                "metric_type": metric_type,
                "period_days": days,
                "trends": sorted(trend_data, key=lambda x: x["date"]),
            }
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get summary statistics for all metric types"""
        from django.db.models import Avg, Count, Max, Min

        summary = {}
        metric_types = PerformanceMetric.METRIC_TYPES

        for metric_type, _ in metric_types:
            metrics = self.queryset.filter(metric_type=metric_type)
            if metrics.exists():
                stats = metrics.aggregate(
                    average=Avg("value"),
                    maximum=Max("value"),
                    minimum=Min("value"),
                    count=Count("id"),
                )
                summary[metric_type] = stats

        return Response(summary)
