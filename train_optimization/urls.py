from django.urls import include, path

urlpatterns = []

# Add REST framework routes only if available
try:
    from rest_framework.routers import DefaultRouter

    from .views import (OptimizationTaskViewSet, PerformanceMetricViewSet,
                        RouteViewSet, ScheduleViewSet, TrainViewSet)

    router = DefaultRouter()
    router.register(r"routes", RouteViewSet)
    router.register(r"trains", TrainViewSet)
    router.register(r"schedules", ScheduleViewSet)
    router.register(r"optimization-tasks", OptimizationTaskViewSet)
    router.register(r"performance-metrics", PerformanceMetricViewSet)

    urlpatterns.append(path("api/v1/", include(router.urls)))
except ImportError:
    # REST framework not available, provide a basic index view
    from django.http import HttpResponse
    from django.views import View

    class IndexView(View):
        def get(self, request):
            return HttpResponse(
                "Transportation Optimization System - Django backend is running"
            )

    urlpatterns.append(path("", IndexView.as_view(), name="index"))
