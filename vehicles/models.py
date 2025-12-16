from django.db import models
from django.utils.translation import gettext_lazy as _
# Use string reference for foreign keys to avoid circular imports during startup if practical,
# but direct import is okay if structure is clean. String ref is safer.

class Vehicle(models.Model):
    class Type(models.TextChoices):
        BASIC = "Basic", _("Basic Life Support")
        ADVANCED = "Advanced", _("Advanced Life Support")
        ICU = "ICU", _("Intensive Care Unit")
        WHEELCHAIR = "Wheelchair", _("Wheelchair Van")

    class Status(models.TextChoices):
        AVAILABLE = "available", _("Available")
        IN_TRIP = "in_trip", _("In Trip")
        MAINTENANCE = "maintenance", _("Maintenance")

    plate_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=20, choices=Type.choices)
    capacity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    odometer_reading = models.FloatField(blank=True, null=True)
    
    # ForeignKey to Company in 'users' app
    vendor_company = models.ForeignKey(
        'users.Company', 
        on_delete=models.CASCADE, 
        related_name='vehicles',
        limit_choices_to={'company_type': 'vendor'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plate_number} ({self.type})"
