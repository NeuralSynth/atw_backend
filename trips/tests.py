"""
Tests for trip management - Fixed with correct Trip model fields.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from trips.models import Trip
from users.models import User
from patients.models import Patient


class TripViewSetTestCase(TestCase):
    """Test trip management endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(username="driver", email="driver@example.com", password="driver123")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Create test patient with correct fields
        self.patient = Patient.objects.create(
            name="John Doe",
            dob="1980-01-01",
        )

    def test_list_trips(self):
        """Test listing all trips."""
        Trip.objects.create(
            patient=self.patient,
            start_location="Location A",
            end_location="Location B",
        )

        url = reverse("trip-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_trip_detail(self):
        """Test retrieving trip details."""
        trip = Trip.objects.create(
            patient=self.patient,
            start_location="Test Location",
            end_location="Test Destination",
        )

        url = reverse("trip-detail", kwargs={"pk": trip.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_location"], "Test Location")
