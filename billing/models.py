from django.db import models
from django.utils.translation import gettext_lazy as _

class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        OVERDUE = "overdue", _("Overdue")

    trip = models.OneToOneField('trips.Trip', on_delete=models.CASCADE, related_name='invoice')
    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='invoices')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)

    @property
    def total(self):
        return self.amount + self.tax

    def __str__(self):
        return f"Invoice {self.id} for Trip {self.trip_id}"

class Contract(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        EXPIRED = "expired", _("Expired")
        TERMINATED = "terminated", _("Terminated")

    class Type(models.TextChoices):
        CLIENT = "client", _("Client")
        VENDOR = "vendor", _("Vendor")

    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='contracts')
    contract_type = models.CharField(max_length=20, choices=Type.choices)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    terms_document_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Contract for {self.company}"

class SystemSettings(models.Model):
    setting_key = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.setting_key
