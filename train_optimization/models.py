from django.db import models
from django.contrib.auth.models import User
import json


class Route(models.Model):
    """Model representing a transportation route"""
    name = models.CharField(max_length=200)
    start_station = models.CharField(max_length=100)
    end_station = models.CharField(max_length=100)
    distance = models.FloatField(help_text="Distance in kilometers")
    estimated_travel_time = models.DurationField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'routes'
        indexes = [
            models.Index(fields=['start_station', 'end_station']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name}: {self.start_station} → {self.end_station}"


class Train(models.Model):
    """Model representing a train"""
    TRAIN_TYPES = [
        ('high_speed', 'High Speed'),
        ('express', 'Express'),
        ('local', 'Local'),
        ('freight', 'Freight'),
    ]
    
    train_id = models.CharField(max_length=20, unique=True)
    train_type = models.CharField(max_length=20, choices=TRAIN_TYPES)
    capacity = models.PositiveIntegerField()
    max_speed = models.FloatField(help_text="Maximum speed in km/h")
    fuel_efficiency = models.FloatField(help_text="Fuel efficiency (km/liter)")
    maintenance_cost_per_km = models.DecimalField(max_digits=10, decimal_places=2)
    is_operational = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trains'
        indexes = [
            models.Index(fields=['train_type']),
            models.Index(fields=['is_operational']),
        ]

    def __str__(self):
        return f"{self.train_id} ({self.train_type})"


class Schedule(models.Model):
    """Model representing train schedules"""
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='schedules')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    passenger_load = models.PositiveIntegerField(default=0)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'schedules'
        indexes = [
            models.Index(fields=['departure_time']),
            models.Index(fields=['arrival_time']),
            models.Index(fields=['train', 'route']),
        ]

    def __str__(self):
        return f"{self.train.train_id} on {self.route.name} at {self.departure_time}"


class OptimizationTask(models.Model):
    """Model representing optimization tasks"""
    TASK_STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    OPTIMIZATION_TYPE = [
        ('schedule', 'Schedule Optimization'),
        ('route', 'Route Optimization'),
        ('fuel', 'Fuel Efficiency'),
        ('multi_objective', 'Multi-Objective'),
    ]
    
    task_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='optimization_tasks')
    optimization_type = models.CharField(max_length=20, choices=OPTIMIZATION_TYPE)
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='pending')
    parameters = models.JSONField(default=dict)
    results = models.JSONField(default=dict)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'optimization_tasks'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['optimization_type']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"Task {self.task_id}: {self.optimization_type} ({self.status})"


class PerformanceMetric(models.Model):
    """Model for storing performance metrics"""
    METRIC_TYPES = [
        ('fuel_consumption', 'Fuel Consumption'),
        ('on_time_performance', 'On-Time Performance'),
        ('passenger_satisfaction', 'Passenger Satisfaction'),
        ('cost_efficiency', 'Cost Efficiency'),
        ('route_utilization', 'Route Utilization'),
    ]
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    train = models.ForeignKey(Train, on_delete=models.CASCADE, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=True, blank=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True, blank=True)
    measured_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'performance_metrics'
        indexes = [
            models.Index(fields=['metric_type', 'measured_at']),
            models.Index(fields=['train', 'measured_at']),
            models.Index(fields=['route', 'measured_at']),
        ]

    def __str__(self):
        return f"{self.metric_type}: {self.value} {self.unit} at {self.measured_at}"
