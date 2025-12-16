from django.db import models

class EMSReport(models.Model):
    trip = models.OneToOneField('trips.Trip', on_delete=models.CASCADE, related_name='ems_report')
    medical_data = models.TextField() # This could be JSONField if using Postgres for more structure
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EMS Report for Trip {self.trip_id}"
