"""
Tests for billing and invoice management.
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal

from billing.models import Invoice, Contract
from users.models import User
from patients.models import Patient


class InvoiceViewSetTestCase(TestCase):
    """Test invoice management."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="billing", email="billing@example.com", password="billing123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.patient = Patient.objects.create(
            first_name="Test",
            last_name="Patient",
            date_of_birth="1990-01-01",
            phone="+1234567890",
        )

    def test_create_invoice(self):
        """Test creating a new invoice."""
        url = reverse("invoice-list")
        data = {
            "patient": self.patient.id,
            "invoice_date": timezone.now().date().isoformat(),
            "due_date": (timezone.now().date() + timezone.timedelta(days=30)).isoformat(),
            "subtotal": "100.00",
            "tax": "15.00",
            "total_amount": "115.00",
            "status": "pending",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Invoice.objects.filter(patient=self.patient).exists())

    def test_list_invoices(self):
        """Test listing all invoices."""
        Invoice.objects.create(
            patient=self.patient,
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=30),
            subtotal=Decimal("100.00"),
            tax=Decimal("15.00"),
            total_amount=Decimal("115.00"),
            status="pending",
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
        self.user = User.objects.create_user(
            username="admin", email="admin@example.com", password="admin123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_contract(self):
        """Test creating a contract."""
        url = reverse("contract-list")
        data = {
            "contract_name": "Test Contract",
            "start_date": timezone.now().date().isoformat(),
            "end_date": (timezone.now().date() + timezone.timedelta(days=365)).isoformat(),
            "status": "active",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Contract.objects.filter(contract_name="Test Contract").exists())
