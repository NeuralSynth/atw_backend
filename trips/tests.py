"""
Tests for trip management and WebSocket consumers.
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path

from trips.models import Trip, ChatMessage
from trips.consumers import GPSTrackingConsumer
from users.models import User
from patients.models import Patient
from vehicles.models import Vehicle


class TripViewSetTestCase(TestCase):
    """Test trip management endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="driver", email="driver@example.com", password="driver123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Create test patient
        self.patient = Patient.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth="1980-01-01",
            phone="+1234567890",
        )

        # Create test vehicle
        self.vehicle = Vehicle.objects.create(
            vehicle_number="AMB-001",
            vehicle_type="ambulance",
            status="available",
        )

    def test_create_trip(self):
        """Test creating a new trip."""
        url = reverse("trip-list")
        data = {
            "patient": self.patient.id,
            "vehicle": self.vehicle.id,
            "driver": self.user.id,
            "pickup_location": "123 Main St",
            "dropoff_location": "456 Hospital Ave",
            "scheduled_pickup_time": timezone.now().isoformat(),
            "status": "pending",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Trip.objects.filter(pickup_location="123 Main St").exists())

    def test_list_trips(self):
        """Test listing all trips."""
        Trip.objects.create(
            patient=self.patient,
            vehicle=self.vehicle,
            driver=self.user,
            pickup_location="Location A",
            dropoff_location="Location B",
            scheduled_pickup_time=timezone.now(),
            status="pending",
        )

        url = reverse("trip-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_trip_status(self):
        """Test updating trip status."""
        trip = Trip.objects.create(
            patient=self.patient,
            vehicle=self.vehicle,
            driver=self.user,
            pickup_location="Location A",
            dropoff_location="Location B",
            scheduled_pickup_time=timezone.now(),
            status="pending",
        )

        url = reverse("trip-detail", kwargs={"pk": trip.pk})
        data = {"status": "in_progress"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trip.refresh_from_db()
        self.assertEqual(trip.status, "in_progress")

    def test_get_trip_detail(self):
        """Test retrieving trip details."""
        trip = Trip.objects.create(
            patient=self.patient,
            vehicle=self.vehicle,
            driver=self.user,
            pickup_location="Test Location",
            dropoff_location="Test Destination",
            scheduled_pickup_time=timezone.now(),
            status="pending",
        )

        url = reverse("trip-detail", kwargs={"pk": trip.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["pickup_location"], "Test Location")


class ChatMessageTestCase(TestCase):
    """Test chat message functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.patient = Patient.objects.create(
            first_name="Jane",
            last_name="Smith",
            date_of_birth="1990-01-01",
            phone="+1111111111",
        )

        self.trip = Trip.objects.create(
            patient=self.patient,
            driver=self.user,
            pickup_location="A",
            dropoff_location="B",
            scheduled_pickup_time=timezone.now(),
            status="pending",
        )

    def test_create_chat_message(self):
        """Test creating a chat message."""
        url = reverse("chatmessage-list")
        data = {
            "trip": self.trip.id,
            "sender": self.user.id,
            "message": "Test message",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ChatMessage.objects.filter(message="Test message").exists()
        )


class GPSTrackingConsumerTestCase(TestCase):
    """Test WebSocket GPS tracking consumer."""

    async def test_websocket_connection(self):
        """Test WebSocket connection to GPS tracking."""
        # Create test data
        user = await User.objects.acreate(
            username="driver", email="driver@example.com"
        )
        patient = await Patient.objects.acreate(
            first_name="Test",
            last_name="Patient",
            date_of_birth="1980-01-01",
            phone="+1234567890",
        )
        trip = await Trip.objects.acreate(
            patient=patient,
            driver=user,
            pickup_location="A",
            dropoff_location="B",
            scheduled_pickup_time=timezone.now(),
            status="in_progress",
        )

        # Create WebSocket communicator
        application = URLRouter(
            [
                re_path(
                    r"^ws/trips/(?P<trip_id>\d+)/gps/$", GPSTrackingConsumer.as_asgi()
                ),
            ]
        )

        communicator = WebsocketCommunicator(
            application, f"/ws/trips/{trip.id}/gps/"
        )

        # Test connection
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Receive connection established message
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "connection_established")
        self.assertEqual(response["trip_id"], str(trip.id))

        # Close connection
        await communicator.disconnect()
