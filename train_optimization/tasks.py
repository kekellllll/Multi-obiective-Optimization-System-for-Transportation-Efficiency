import logging
import uuid

from celery import shared_task
from django.utils import timezone

from .models import OptimizationTask
from .optimization import MultiObjectiveOptimizer

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_optimization_task(self, task_id, optimization_type, parameters):
    """
    Celery task for running optimization algorithms in the background
    """
    try:
        # Update task status to running
        task = OptimizationTask.objects.get(task_id=task_id)
        task.status = "running"
        task.start_time = timezone.now()
        task.save()

        # Initialize optimizer
        optimizer = MultiObjectiveOptimizer()

        # Run optimization based on type
        if optimization_type == "dqn":
            results = optimizer.optimize({"optimization_type": "dqn", **parameters})
        elif optimization_type == "multi_objective":
            results = optimizer.nsga2_optimization(parameters)
        else:
            # Use the main optimize method which handles routing
            results = optimizer.optimize({"optimization_type": optimization_type, **parameters})

        # Update task with results
        task.status = "completed"
        task.end_time = timezone.now()
        task.results = results
        task.save()

        logger.info(f"Optimization task {task_id} completed successfully")
        return results

    except Exception as exc:
        # Update task status to failed
        task = OptimizationTask.objects.get(task_id=task_id)
        task.status = "failed"
        task.end_time = timezone.now()
        task.error_message = str(exc)
        task.save()

        logger.error(f"Optimization task {task_id} failed: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task
def collect_performance_metrics():
    """
    Periodic task to collect and store performance metrics
    """
    import random
    from datetime import datetime, timedelta

    from .models import PerformanceMetric, Route, Schedule, Train

    try:
        # Simulate collecting metrics for all active trains and routes
        trains = Train.objects.filter(is_operational=True)
        routes = Route.objects.filter(is_active=True)

        current_time = timezone.now()

        # Generate simulated metrics
        for train in trains:
            # Fuel consumption metric
            PerformanceMetric.objects.create(
                metric_type="fuel_consumption",
                value=random.uniform(8, 15),  # km/liter
                unit="km/liter",
                train=train,
                measured_at=current_time,
            )

            # On-time performance
            PerformanceMetric.objects.create(
                metric_type="on_time_performance",
                value=random.uniform(85, 98),  # percentage
                unit="percentage",
                train=train,
                measured_at=current_time,
            )

        for route in routes:
            # Route utilization
            PerformanceMetric.objects.create(
                metric_type="route_utilization",
                value=random.uniform(60, 90),  # percentage
                unit="percentage",
                route=route,
                measured_at=current_time,
            )

        logger.info(f"Performance metrics collected at {current_time}")
        return f"Collected metrics for {len(trains)} trains and {len(routes)} routes"

    except Exception as exc:
        logger.error(f"Failed to collect performance metrics: {exc}")
        raise


@shared_task
def cleanup_old_optimization_tasks():
    """
    Periodic task to clean up old optimization tasks
    """
    from datetime import timedelta

    try:
        cutoff_date = timezone.now() - timedelta(days=30)

        # Delete old completed tasks
        deleted_count = OptimizationTask.objects.filter(
            status="completed", created_at__lt=cutoff_date
        ).delete()[0]

        logger.info(f"Cleaned up {deleted_count} old optimization tasks")
        return f"Cleaned up {deleted_count} old tasks"

    except Exception as exc:
        logger.error(f"Failed to cleanup old tasks: {exc}")
        raise


@shared_task
def generate_optimization_report():
    """
    Generate periodic optimization reports
    """
    from django.conf import settings
    from django.core.mail import send_mail

    from .optimization import PerformanceAnalyzer

    try:
        # Generate dashboard metrics
        metrics = PerformanceAnalyzer.generate_dashboard_metrics()

        # Create report content
        report_content = f"""
        Transportation Optimization System - Weekly Report
        
        Key Metrics:
        - Total Operational Trains: {metrics['total_trains']}
        - Active Routes: {metrics['active_routes']}
        - Scheduled Trips: {metrics['scheduled_trips']}
        - Average Fuel Efficiency: {metrics['avg_fuel_efficiency']:.2f} km/liter
        - On-Time Performance: {metrics['on_time_performance']:.1f}%
        - Total Passengers: {metrics['total_passengers']:,}
        - Estimated Cost Savings: ${metrics['cost_savings']:,.2f}
        - Optimization Tasks Completed: {metrics['optimization_tasks_completed']}
        
        Generated at: {timezone.now()}
        """

        # Log the report (in a real system, you might send this via email)
        logger.info(f"Generated optimization report: {report_content}")

        return "Optimization report generated successfully"

    except Exception as exc:
        logger.error(f"Failed to generate optimization report: {exc}")
        raise
