from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Trip(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        ASSIGNED = "assigned", _("Assigned")
        EN_ROUTE = "en_route", _("En Route")
        AT_PICKUP = "at_pickup", _("At Pickup")
        IN_TRANSIT = "in_transit", _("In Transit")
        ARRIVED = "arrived", _("Arrived")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    class Source(models.TextChoices):
        PHONE = "phone", _("Phone")
        ONLINE = "online", _("Online")
        APP = "app", _("App")
        CONTRACT = "contract", _("Contract")

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="trips", blank=True, null=True)
    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.SET_NULL, related_name="trips", blank=True, null=True)

    # Drivers and Paramedics are Users
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="driven_trips",
        blank=True,
        null=True,
        limit_choices_to={"role": "Driver"},
    )
    paramedic = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="medic_trips",
        blank=True,
        null=True,
        limit_choices_to={"role": "Paramedic"},
    )

    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    start_odometer = models.FloatField(blank=True, null=True)
    end_odometer = models.FloatField(blank=True, null=True)

    request_source = models.CharField(max_length=20, choices=Source.choices, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_distance(self):
        if self.end_odometer is not None and self.start_odometer is not None:
            return self.end_odometer - self.start_odometer
        return None

    def __str__(self):
        return f"Trip {self.id} - {self.status}"


class ChatMessage(models.Model):
    class Type(models.TextChoices):
        TEXT = "text", _("Text")
        IMAGE = "image", _("Image")
        SYSTEM = "system", _("System")

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="chat_messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")

    message_content = models.TextField()
    message_type = models.CharField(max_length=10, choices=Type.choices, default=Type.TEXT)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg {self.id} from {self.sender}"
