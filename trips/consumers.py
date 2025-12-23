"""
WebSocket consumers for real-time GPS tracking and trip status updates.

Provides 3-5 second GPS updates to connected clients.
"""

import json

from asgiref.sync import sync_to_async  # noqa: F401
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class GPSTrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time GPS tracking.

    Clients connect to: ws://api.atw.com/ws/trips/<trip_id>/gps/
    Receives GPS updates every 3-5 seconds.
    """

    async def connect(self):
        """Accept WebSocket connection and join trip group."""
        self.trip_id = self.scope["url_route"]["kwargs"]["trip_id"]
        self.trip_group_name = f"trip_gps_{self.trip_id}"

        # Join trip-specific group
        await self.channel_layer.group_add(self.trip_group_name, self.channel_name)

        await self.accept()

        # Send initial trip data
        trip_data = await self.get_trip_data()
        await self.send(text_data=json.dumps({"type": "connection_established", "trip_id": self.trip_id, "data": trip_data}))

    async def disconnect(self, close_code):
        """Leave trip group on disconnect."""
        await self.channel_layer.group_discard(self.trip_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receive GPS update from driver mobile app.
        Broadcast to all clients tracking this trip.
        """
        try:
            data = json.loads(text_data)

            if data.get("type") == "gps_update":
                # Validate and save GPS data
                await self.save_gps_location(
                    trip_id=self.trip_id,
                    latitude=data.get("latitude"),
                    longitude=data.get("longitude"),
                    speed=data.get("speed"),
                    heading=data.get("heading"),
                    timestamp=data.get("timestamp"),
                )

                # Broadcast to all clients tracking this trip
                await self.channel_layer.group_send(
                    self.trip_group_name,
                    {
                        "type": "gps_location_update",
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "speed": data.get("speed"),
                        "heading": data.get("heading"),
                        "timestamp": data.get("timestamp"),
                    },
                )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"type": "error", "message": "Invalid JSON data"}))
        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def gps_location_update(self, event):
        """
        Handler for GPS location update events.
        Sends GPS data to WebSocket client.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "gps_update",
                    "trip_id": self.trip_id,
                    "latitude": event["latitude"],
                    "longitude": event["longitude"],
                    "speed": event.get("speed"),
                    "heading": event.get("heading"),
                    "timestamp": event["timestamp"],
                }
            )
        )

    @database_sync_to_async
    def get_trip_data(self):
        """Get initial trip data from database."""
        from trips.models import Trip

        try:
            trip = Trip.objects.select_related("driver", "vehicle", "patient").get(id=self.trip_id)
            return {
                "id": trip.id,
                "status": trip.status,
                "driver": {
                    "id": trip.driver.id if trip.driver else None,
                    "name": trip.driver.get_full_name() if trip.driver else None,
                },
                "vehicle": {
                    "id": trip.vehicle.id if trip.vehicle else None,
                    "name": trip.vehicle.vehicle_number if trip.vehicle else None,
                },
                "pickup_location": trip.pickup_location,
                "dropoff_location": trip.dropoff_location,
            }
        except Trip.DoesNotExist:
            return None

    @database_sync_to_async
    def save_gps_location(self, trip_id, latitude, longitude, speed=None, heading=None, timestamp=None):
        """Save GPS location to database."""
        from django.utils import timezone

        from trips.models import Trip

        try:
            trip = Trip.objects.get(id=trip_id)

            # Update trip's current location
            trip.current_latitude = latitude
            trip.current_longitude = longitude
            trip.last_gps_update = timestamp or timezone.now()
            trip.save(update_fields=["current_latitude", "current_longitude", "last_gps_update"])

            # Optionally: Save to GPS tracking history table
            # GPSTrackingHistory.objects.create(...)

        except Trip.DoesNotExist:
            pass


class TripStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for trip status updates.

    Notifies clients when trip status changes (assigned, en_route, completed, etc.)
    """

    async def connect(self):
        """Accept WebSocket connection and join trip status group."""
        self.trip_id = self.scope["url_route"]["kwargs"]["trip_id"]
        self.trip_status_group = f"trip_status_{self.trip_id}"

        await self.channel_layer.group_add(self.trip_status_group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """Leave trip status group on disconnect."""
        await self.channel_layer.group_discard(self.trip_status_group, self.channel_name)

    async def trip_status_change(self, event):
        """Send trip status change to WebSocket client."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "status_update",
                    "trip_id": self.trip_id,
                    "status": event["status"],
                    "timestamp": event["timestamp"],
                    "message": event.get("message"),
                }
            )
        )
