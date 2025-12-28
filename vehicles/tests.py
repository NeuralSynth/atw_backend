"""
Tests for vehicle management - Fixed to match actual Vehicle model.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from users.models import Company, User
from vehicles.models import Vehicle


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

        # Create a vendor company (required for vehicle)
        self.company = Company.objects.create(
            company_name="Test Vendor",
            company_type=Company.Type.VENDOR,
        )

    def test_create_vehicle(self):
        """Test creating a new vehicle - API test."""
        url = reverse("vehicle-list")
        data = {
            "plate_number": "AMB-101",
            "type": Vehicle.Type.BASIC,
            "vendor_company": self.company.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Vehicle.objects.filter(plate_number="AMB-101").exists())

    def test_list_vehicles(self):
        """Test listing all vehicles."""
        Vehicle.objects.create(
            plate_number="AMB-201",
            type=Vehicle.Type.BASIC,
            vendor_company=self.company,
        )
        Vehicle.objects.create(
            plate_number="AMB-202",
            type=Vehicle.Type.ADVANCED,
            vendor_company=self.company,
        )

        url = reverse("vehicle-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_vehicle_status(self):
        """Test updating vehicle status."""
        vehicle = Vehicle.objects.create(
            plate_number="AMB-301",
            type=Vehicle.Type.BASIC,
            vendor_company=self.company,
        )

        url = reverse("vehicle-detail", kwargs={"pk": vehicle.pk})
        data = {"status": Vehicle.Status.IN_TRIP}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.status, Vehicle.Status.IN_TRIP)

    def test_get_vehicle_detail(self):
        """Test retrieving vehicle details."""
        vehicle = Vehicle.objects.create(
            plate_number="AMB-401",
            type=Vehicle.Type.ICU,
            model="Mercedes Sprinter",
            vendor_company=self.company,
        )

        url = reverse("vehicle-detail", kwargs={"pk": vehicle.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["plate_number"], "AMB-401")
