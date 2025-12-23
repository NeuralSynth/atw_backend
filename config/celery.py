"""
Celery configuration for ATW Backend.

Handles async tasks like:
- GPS data processing
- Email notifications
- Report generation
- Background jobs
"""

import os

from celery import Celery

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Create Celery app
app = Celery("atw_backend")

# Load configuration from Django settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Task routing configuration
app.conf.task_routes = {
    "trips.tasks.broadcast_gps_update": {"queue": "high_priority"},
    "trips.tasks.process_trip_completion": {"queue": "normal"},
    "billing.tasks.generate_invoice": {"queue": "normal"},
    "users.tasks.send_notification": {"queue": "low_priority"},
}

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    "cleanup-old-gps-data": {
        "task": "trips.tasks.cleanup_old_gps_data",
        "schedule": 3600.0,  # Every hour
    },
    "check-trip-timeouts": {
        "task": "trips.tasks.check_trip_timeouts",
        "schedule": 300.0,  # Every 5 minutes
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f"Request: {self.request!r}")
