"""
Tests for patient management - Fixed to match actual Patient model.
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
        self.user = User.objects.create_user(username="staff", email="staff@example.com", password="staff123")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_patient(self):
        """Test creating a new patient."""
        url = reverse("patient-list")
        data = {
            "name": "Alice Johnson",
            "medical_record_number": "MRN-12345",
            "dob": "1985-05-15",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Patient.objects.filter(name="Alice Johnson").exists())

    def test_list_patients(self):
        """Test listing all patients."""
        Patient.objects.create(
            name="Bob Smith",
            dob="1990-01-01",
        )
        Patient.objects.create(
            name="Carol Brown",
            dob="1975-12-31",
        )

        url = reverse("patient-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_patient_detail(self):
        """Test retrieving patient details."""
        patient = Patient.objects.create(
            name="David Wilson",
            dob="1988-07-20",
        )

        url = reverse("patient-detail", kwargs={"pk": patient.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "David Wilson")

    def test_update_patient(self):
        """Test updating patient information."""
        patient = Patient.objects.create(
            name="Eve Davis",
            dob="1992-03-10",
        )

        url = reverse("patient-detail", kwargs={"pk": patient.pk})
        data = {"name": "Eve Davis-Smith"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient.refresh_from_db()
        self.assertEqual(patient.name, "Eve Davis-Smith")

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access patients."""
        self.client.credentials()  # Remove authentication
        url = reverse("patient-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
