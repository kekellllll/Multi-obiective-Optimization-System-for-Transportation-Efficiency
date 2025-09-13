import os

try:
    from celery import Celery

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

    # Mock Celery for environments where it's not available
    class Celery:
        def __init__(self, *args, **kwargs):
            pass

        def config_from_object(self, *args, **kwargs):
            pass

        def autodiscover_tasks(self, *args, **kwargs):
            pass

        def task(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator


from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "transportation_optimization_backend.settings"
)

app = Celery("transportation_optimization_backend")

if CELERY_AVAILABLE:
    # Using a string here means the worker doesn't have to serialize
    # the configuration object to child processes.
    app.config_from_object("django.conf:settings", namespace="CELERY")

    # Load task modules from all registered Django apps.
    app.autodiscover_tasks()

    # Configure periodic tasks
    app.conf.beat_schedule = {
        "collect-performance-metrics": {
            "task": "train_optimization.tasks.collect_performance_metrics",
            "schedule": 300.0,  # Every 5 minutes
        },
        "cleanup-old-tasks": {
            "task": "train_optimization.tasks.cleanup_old_optimization_tasks",
            "schedule": 86400.0,  # Every 24 hours
        },
        "generate-optimization-report": {
            "task": "train_optimization.tasks.generate_optimization_report",
            "schedule": 604800.0,  # Every week
        },
    }

    app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
