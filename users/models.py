from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "Admin", _("Admin")
        DRIVER = "Driver", _("Driver")
        PARAMEDIC = "Paramedic", _("Paramedic")
        CORPORATE = "Corporate", _("Corporate")
        VENDOR = "Vendor", _("Vendor")

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMIN)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # We can remove username requirement if we want email login, but forcing username=email is easier for now
    # or just keep standard django username. Let's keep standard for simplicity unless SRS forces email login.
    # SRS implies login, usually email. Let's ensure email is unique.
    email = models.EmailField(_('email address'), unique=True)

    REQUIRED_FIELDS = ['email', 'role']

    def __str__(self):
        return f"{self.username} ({self.role})"

class Company(models.Model):
    class Type(models.TextChoices):
        CLIENT = "client", _("Client")
        VENDOR = "vendor", _("Vendor")

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")

    company_name = models.CharField(max_length=255)
    company_type = models.CharField(max_length=10, choices=Type.choices)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self):
        return self.company_name
