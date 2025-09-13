from django.contrib import admin

from .models import OptimizationTask, PerformanceMetric, Route, Schedule, Train


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_station",
        "end_station",
        "distance",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "start_station", "end_station")
    search_fields = ("name", "start_station", "end_station")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = (
        "train_id",
        "train_type",
        "capacity",
        "max_speed",
        "fuel_efficiency",
        "is_operational",
    )
    list_filter = ("train_type", "is_operational")
    search_fields = ("train_id", "train_type")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "train",
        "route",
        "departure_time",
        "arrival_time",
        "passenger_load",
        "is_cancelled",
    )
    list_filter = ("is_cancelled", "departure_time", "train__train_type")
    search_fields = ("train__train_id", "route__name")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "departure_time"


@admin.register(OptimizationTask)
class OptimizationTaskAdmin(admin.ModelAdmin):
    list_display = (
        "task_id",
        "user",
        "optimization_type",
        "status",
        "start_time",
        "end_time",
    )
    list_filter = ("status", "optimization_type", "created_at")
    search_fields = ("task_id", "user__username")
    readonly_fields = ("task_id", "created_at", "updated_at", "start_time", "end_time")

    def has_change_permission(self, request, obj=None):
        # Prevent editing of running tasks
        if obj and obj.status == "running":
            return False
        return super().has_change_permission(request, obj)


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ("metric_type", "value", "unit", "train", "route", "measured_at")
    list_filter = ("metric_type", "measured_at", "unit")
    search_fields = ("metric_type", "train__train_id", "route__name")
    readonly_fields = ("created_at",)
    date_hierarchy = "measured_at"
