"""
Tests for patient management.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from patients.models import Patient
from users.models import User


class PatientViewSetTestCase(TestCase):
    """Test patient CRUD operations."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="staff", email="staff@example.com", password="staff123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_patient(self):
        """Test creating a new patient."""
        url = reverse("patient-list")
        data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "date_of_birth": "1985-05-15",
            "phone": "+1234567890",
            "email": "alice@example.com",
            "address": "789 Patient Rd",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Patient.objects.filter(first_name="Alice").exists())

    def test_list_patients(self):
        """Test listing all patients."""
        Patient.objects.create(
            first_name="Bob",
            last_name="Smith",
            date_of_birth="1990-01-01",
            phone="+1111111111",
        )
        Patient.objects.create(
            first_name="Carol",
            last_name="Brown",
            date_of_birth="1975-12-31",
            phone="+2222222222",
        )

        url = reverse("patient-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_patient_detail(self):
        """Test retrieving patient details."""
        patient = Patient.objects.create(
            first_name="David",
            last_name="Wilson",
            date_of_birth="1988-07-20",
            phone="+3333333333",
        )

        url = reverse("patient-detail", kwargs={"pk": patient.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "David")

    def test_update_patient(self):
        """Test updating patient information."""
        patient = Patient.objects.create(
            first_name="Eve",
            last_name="Davis",
            date_of_birth="1992-03-10",
            phone="+4444444444",
        )

        url = reverse("patient-detail", kwargs={"pk": patient.pk})
        data = {"phone": "+5555555555"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient.refresh_from_db()
        self.assertEqual(patient.phone, "+5555555555")

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access patients."""
        self.client.credentials()  # Remove authentication
        url = reverse("patient-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patient_phone_required(self):
        """Test that phone number is required for patient creation."""
        url = reverse("patient-list")
        data = {
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            # Missing phone
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
