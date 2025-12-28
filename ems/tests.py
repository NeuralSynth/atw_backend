"""
Tests for EMS compliance and reporting - Fixed with correct Trip fields.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ems.models import EMSReport
from patients.models import Patient
from trips.models import Trip
from users.models import User


class EMSReportTestCase(TestCase):
    """Test EMS report management."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(username="ems_staff", email="ems@example.com", password="ems123")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.patient = Patient.objects.create(
            name="EMS Patient",
            dob="1980-01-01",
        )

        self.trip = Trip.objects.create(
            patient=self.patient,
            start_location="Emergency Site",
            end_location="Hospital",
        )

    def test_list_ems_reports(self):
        """Test listing EMS reports."""
        EMSReport.objects.create(
            trip=self.trip,
        )

        url = reverse("emsreport-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
