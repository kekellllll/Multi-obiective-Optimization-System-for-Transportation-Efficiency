from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RouteViewSet, TrainViewSet, ScheduleViewSet,
    OptimizationTaskViewSet, PerformanceMetricViewSet
)

router = DefaultRouter()
router.register(r'routes', RouteViewSet)
router.register(r'trains', TrainViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'optimization-tasks', OptimizationTaskViewSet)
router.register(r'performance-metrics', PerformanceMetricViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]