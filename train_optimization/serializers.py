from rest_framework import serializers

from .models import OptimizationTask, PerformanceMetric, Route, Schedule, Train


class RouteSerializer(serializers.ModelSerializer):
    """Serializer for Route model"""

    class Meta:
        model = Route
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class TrainSerializer(serializers.ModelSerializer):
    """Serializer for Train model"""

    class Meta:
        model = Train
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Schedule model"""

    train_details = TrainSerializer(source="train", read_only=True)
    route_details = RouteSerializer(source="route", read_only=True)

    class Meta:
        model = Schedule
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class ScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Schedule instances"""

    class Meta:
        model = Schedule
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class OptimizationTaskSerializer(serializers.ModelSerializer):
    """Serializer for OptimizationTask model"""

    user_name = serializers.CharField(source="user.username", read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = OptimizationTask
        fields = "__all__"
        read_only_fields = (
            "task_id",
            "user",
            "start_time",
            "end_time",
            "created_at",
            "updated_at",
        )

    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            return (obj.end_time - obj.start_time).total_seconds()
        return None


class OptimizationTaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating OptimizationTask instances"""

    class Meta:
        model = OptimizationTask
        fields = ("optimization_type", "parameters")


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """Serializer for PerformanceMetric model"""

    train_details = TrainSerializer(source="train", read_only=True)
    route_details = RouteSerializer(source="route", read_only=True)

    class Meta:
        model = PerformanceMetric
        fields = "__all__"
        read_only_fields = ("created_at",)


class PerformanceMetricCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PerformanceMetric instances"""

    class Meta:
        model = PerformanceMetric
        fields = "__all__"
        read_only_fields = ("created_at",)


class OptimizationResultSerializer(serializers.Serializer):
    """Serializer for optimization results"""

    objective_values = serializers.DictField(child=serializers.FloatField())
    optimal_schedules = serializers.ListField(child=serializers.DictField())
    performance_improvements = serializers.DictField(child=serializers.FloatField())
    recommendations = serializers.ListField(child=serializers.CharField())


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics"""

    total_trains = serializers.IntegerField()
    active_routes = serializers.IntegerField()
    scheduled_trips = serializers.IntegerField()
    avg_fuel_efficiency = serializers.FloatField()
    on_time_performance = serializers.FloatField()
    total_passengers = serializers.IntegerField()
    cost_savings = serializers.FloatField()
    optimization_tasks_completed = serializers.IntegerField()
