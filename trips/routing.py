"""
WebSocket routing for real-time GPS tracking.
"""

from django.urls import path

from trips import consumers

websocket_urlpatterns = [
    # GPS tracking WebSocket endpoint
    # URL: ws://api.atw.com/ws/trips/<trip_id>/gps/
    path("ws/trips/<int:trip_id>/gps/", consumers.GPSTrackingConsumer.as_asgi()),
    # Trip status updates WebSocket
    # URL: ws://api.atw.com/ws/trips/<trip_id>/status/
    path("ws/trips/<int:trip_id>/status/", consumers.TripStatusConsumer.as_asgi()),
]
