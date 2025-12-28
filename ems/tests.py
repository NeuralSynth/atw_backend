"""
Tests for EMS compliance and reporting.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from ems.models import EMSReport
from users.models import User
from trips.models import Trip
from patients.models import Patient


class EMSReportTestCase(TestCase):
    """Test EMS report management."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="ems_staff", email="ems@example.com", password="ems123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.patient = Patient.objects.create(
            first_name="EMS",
            last_name="Patient",
            date_of_birth="1980-01-01",
            phone="+1234567890",
        )

        self.trip = Trip.objects.create(
            patient=self.patient,
            driver=self.user,
            pickup_location="Emergency Site",
            dropoff_location="Hospital",
            status="completed",
        )

    def test_create_ems_report(self):
        """Test creating an EMS report."""
        url = reverse("emsreport-list")
        data = {
            "trip": self.trip.id,
            "report_type": "Emergency Transport",
            "notes": "Patient transported with oxygen support",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(EMSReport.objects.filter(trip=self.trip).exists())

    def test_list_ems_reports(self):
        """Test listing EMS reports."""
        EMSReport.objects.create(
            trip=self.trip,
            report_type="Emergency",
            notes="Test report",
        )

        url = reverse("emsreport-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
