"""
Celery background tasks for trip management.

Handles GPS tracking, trip monitoring, and cleanup operations.
"""

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from datetime import timedelta


@shared_task(queue="high_priority")
def broadcast_gps_update(trip_id, latitude, longitude, speed=None, heading=None):
    """
    Broadcast GPS update to all clients tracking a trip.

    High priority task for real-time GPS tracking.

    Args:
        trip_id: Trip ID
        latitude: GPS latitude
        longitude: GPS longitude
        speed: Vehicle speed (optional)
        heading: Vehicle heading (optional)
    """
    channel_layer = get_channel_layer()
    trip_group_name = f"trip_gps_{trip_id}"

    async_to_sync(channel_layer.group_send)(
        trip_group_name,
        {
            "type": "gps_location_update",
            "latitude": latitude,
            "longitude": longitude,
            "speed": speed,
            "heading": heading,
            "timestamp": timezone.now().isoformat(),
        },
    )

    return f"GPS update broadcast for trip {trip_id}"


@shared_task(queue="high_priority")
def broadcast_trip_status(trip_id, status, message=None):
    """
    Broadcast trip status change to all clients.

    Args:
        trip_id: Trip ID
        status: New trip status
        message: Optional status message
    """
    channel_layer = get_channel_layer()
    trip_status_group = f"trip_status_{trip_id}"

    async_to_sync(channel_layer.group_send)(
        trip_status_group,
        {
            "type": "trip_status_change",
            "status": status,
            "timestamp": timezone.now().isoformat(),
            "message": message,
        },
    )

    return f"Status update broadcast for trip {trip_id}: {status}"


@shared_task
def cleanup_old_gps_data():
    """
    Periodic task to cleanup old GPS tracking data.

    Runs every hour (configured in config/celery.py).
    Removes GPS data older than 30 days to save storage.
    """
    from trips.models import Trip

    cutoff_date = timezone.now() - timedelta(days=30)

    # Clear GPS data from old completed trips
    updated_count = Trip.objects.filter(
        status__in=["completed", "cancelled"],
        updated_at__lt=cutoff_date,
    ).update(
        current_latitude=None,
        current_longitude=None,
    )

    return f"Cleaned up GPS data from {updated_count} old trips"


@shared_task
def check_trip_timeouts():
    """
    Periodic task to check for trip timeouts.

    Runs every 5 minutes (configured in config/celery.py).
    Flags trips that have been in progress for too long.
    """
    from trips.models import Trip

    # Check for in-progress trips older than 6 hours
    timeout_threshold = timezone.now() - timedelta(hours=6)

    timeout_trips = Trip.objects.filter(
        status="in_progress",
        started_at__lt=timeout_threshold,
    )

    flagged_count = 0
    for trip in timeout_trips:
        # Flag as requiring attention
        trip.notes = f"{trip.notes or ''}\n[TIMEOUT ALERT] Trip exceeded 6 hour threshold"
        trip.save(update_fields=["notes", "updated_at"])
        flagged_count += 1

        # Optionally: Send notification to dispatcher
        # send_notification.delay(...)

    return f"Flagged {flagged_count} trips exceeding timeout threshold"


@shared_task(queue="normal")
def process_trip_completion(trip_id):
    """
    Handle trip completion workflow.

    Triggered when a trip is marked as completed.
    - Generate invoice
    - Send completion notifications
    - Update vehicle availability

    Args:
        trip_id: ID of the completed trip
    """
    from trips.models import Trip
    from billing.tasks import generate_invoice
    from users.tasks import send_notification

    try:
        trip = Trip.objects.select_related("patient", "driver", "vehicle").get(id=trip_id)

        # Generate invoice for the trip
        generate_invoice.delay(trip_id)

        # Send completion notification to patient
        if trip.patient and trip.patient.email:
            send_notification.delay(
                user_id=trip.patient.id,
                notification_type="trip_completed",
                message=f"Your trip #{trip_id} has been completed.",
            )

        # Update vehicle availability
        if trip.vehicle:
            trip.vehicle.status = "available"
            trip.vehicle.save(update_fields=["status"])

        # Update driver availability
        if trip.driver:
            trip.driver.driver_status = "available"
            trip.driver.save(update_fields=["driver_status"])

        return f"Trip {trip_id} completion processed successfully"

    except Trip.DoesNotExist:
        return f"Trip {trip_id} not found"
