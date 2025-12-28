"""
Tests for vehicle management.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from vehicles.models import Vehicle
from users.models import User


class VehicleViewSetTestCase(TestCase):
    """Test vehicle CRUD operations."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="fleet_manager",
            email="manager@example.com",
            password="manager123",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_vehicle(self):
        """Test creating a new vehicle."""
        url = reverse("vehicle-list")
        data = {
            "vehicle_number": "AMB-101",
            "vehicle_type": "ambulance",
            "make": "Ford",
            "model": "Transit",
            "year": 2023,
            "status": "available",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Vehicle.objects.filter(vehicle_number="AMB-101").exists())

    def test_list_vehicles(self):
        """Test listing all vehicles."""
        Vehicle.objects.create(
            vehicle_number="AMB-201",
            vehicle_type="ambulance",
            status="available",
        )
        Vehicle.objects.create(
            vehicle_number="AMB-202",
            vehicle_type="ambulance",
            status="in_use",
        )

        url = reverse("vehicle-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_vehicle_status(self):
        """Test updating vehicle status."""
        vehicle = Vehicle.objects.create(
            vehicle_number="AMB-301",
            vehicle_type="ambulance",
            status="available",
        )

        url = reverse("vehicle-detail", kwargs={"pk": vehicle.pk})
        data = {"status": "in_use"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.status, "in_use")

    def test_get_vehicle_detail(self):
        """Test retrieving vehicle details."""
        vehicle = Vehicle.objects.create(
            vehicle_number="AMB-401",
            vehicle_type="ambulance",
            make="Mercedes",
            model="Sprinter",
            year=2022,
            status="available",
        )

        url = reverse("vehicle-detail", kwargs={"pk": vehicle.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["vehicle_number"], "AMB-401")
        self.assertEqual(response.data["make"], "Mercedes")
