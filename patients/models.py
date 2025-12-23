from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=255)
    medical_record_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

    # ForeignKey to Company (Client who owns the patient record)
    company = models.ForeignKey(
        "users.Company",
        on_delete=models.CASCADE,
        related_name="patients",
        limit_choices_to={"company_type": "client"},
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
