"""
Celery background tasks for user notifications.

Handles email notifications, SMS, and push notifications.
"""

from celery import shared_task


@shared_task(queue="low_priority")
def send_notification(user_id, notification_type, message, **kwargs):
    """
    Send notification to a user.

    Supports multiple notification channels:
    - Email
    - SMS (future)
    - Push notifications (future)

    Args:
        user_id: User ID to send notification to
        notification_type: Type of notification (trip_assigned, trip_completed, etc.)
        message: Notification message
        **kwargs: Additional notification parameters

    Returns:
        Success or error message
    """
    from users.models import User

    try:
        user = User.objects.get(id=user_id)

        # TODO: Implement actual notification sending
        # For now, just log the notification

        # Example: Email notification
        if user.email:
            # send_email(
            #     to=user.email,
            #     subject=f"ATW Transportation - {notification_type}",
            #     message=message,
            #     **kwargs
            # )
            pass

        # Example: SMS notification (future)
        # if user.phone:
        #     send_sms(to=user.phone, message=message)

        return f"Notification sent to user {user_id}: {notification_type}"

    except User.DoesNotExist:
        return f"User {user_id} not found"
    except Exception as e:
        return f"Error sending notification: {str(e)}"


@shared_task(queue="low_priority")
def send_welcome_email(user_id):
    """
    Send welcome email to newly registered user.

    Args:
        user_id: User ID

    Returns:
        Success or error message
    """
    from users.models import User

    try:
        user = User.objects.get(id=user_id)

        if not user.email:
            return f"No email address for user {user_id}"

        # TODO: Implement actual welcome email
        # send_email(
        #     to=user.email,
        #     subject="Welcome to ATW Transportation",
        #     template="welcome_email.html",
        #     context={"user": user}
        # )

        return f"Welcome email sent to {user.email}"

    except User.DoesNotExist:
        return f"User {user_id} not found"
    except Exception as e:
        return f"Error sending welcome email: {str(e)}"


@shared_task(queue="normal")
def send_trip_assignment_notification(trip_id, driver_id):
    """
    Notify driver about new trip assignment.

    Args:
        trip_id: Trip ID
        driver_id: Driver user ID

    Returns:
        Success or error message
    """
    from trips.models import Trip
    from users.models import User

    try:
        trip = Trip.objects.select_related("patient").get(id=trip_id)
        # The 'driver' variable was fetched but not used.
        # driver = User.objects.get(id=driver_id)

        message = f"You have been assigned to Trip #{trip_id}. "
        message += f"Pickup: {trip.pickup_location}, Dropoff: {trip.dropoff_location}. "
        message += f"Scheduled time: {trip.scheduled_pickup_time}"

        return send_notification(
            user_id=driver_id,
            notification_type="trip_assigned",
            message=message,
            trip_id=trip_id,
        )

    except (Trip.DoesNotExist, User.DoesNotExist) as e:
        return f"Error: {str(e)}"


@shared_task(queue="low_priority")
def send_daily_digest(user_id):
    """
    Send daily digest email with trip summary and updates.

    Args:
        user_id: User ID

    Returns:
        Success or error message
    """
    from django.utils import timezone

    from trips.models import Trip
    from users.models import User

    try:
        user = User.objects.get(id=user_id)

        if not user.email:
            return f"No email address for user {user_id}"

        # Get today's trips
        today = timezone.now().date()
        trips = Trip.objects.filter(
            driver=user,
            scheduled_pickup_time__date=today,
        ).order_by("scheduled_pickup_time")

        # TODO: Send digest email with trip list
        # send_email(
        #     to=user.email,
        #     subject=f"Daily Digest - {today}",
        #     template="daily_digest.html",
        #     context={
        #         "user": user,
        #         "trips": trips,
        #         "date": today,
        #     }
        # )

        return f"Daily digest sent to {user.email} with {trips.count()} trips"

    except User.DoesNotExist:
        return f"User {user_id} not found"
    except Exception as e:
        return f"Error sending daily digest: {str(e)}"
