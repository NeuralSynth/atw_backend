"""
Tests for billing and invoice management - Fixed with correct Trip fields.
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from billing.models import Contract, Invoice
from patients.models import Patient
from trips.models import Trip
from users.models import Company, User


class InvoiceViewSetTestCase(TestCase):
    """Test invoice management."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(username="billing", email="billing@example.com", password="billing123")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.company = Company.objects.create(
            company_name="Test Client",
            company_type=Company.Type.CLIENT,
        )

        self.patient = Patient.objects.create(
            name="Test Patient",
            dob="1990-01-01",
        )

        self.trip = Trip.objects.create(
            patient=self.patient,
            start_location="123 Main St",
            end_location="456 Hospital Ave",
        )

    def test_list_invoices(self):
        """Test listing all invoices."""
        Invoice.objects.create(
            trip=self.trip,
            company=self.company,
            amount=Decimal("100.00"),
            tax=Decimal("15.00"),
        )

        url = reverse("invoice-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class ContractTestCase(TestCase):
    """Test contract management."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(username="admin", email="admin@example.com", password="admin123")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.company = Company.objects.create(
            company_name="Test Company",
            company_type=Company.Type.CLIENT,
        )

    def test_create_contract(self):
        """Test creating a contract."""
        url = reverse("contract-list")
        data = {
            "company": self.company.id,
            "contract_type": Contract.Type.CLIENT,
            "start_date": timezone.now().isoformat(),
            "end_date": (timezone.now() + timezone.timedelta(days=365)).isoformat(),
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Contract.objects.filter(company=self.company).exists())
