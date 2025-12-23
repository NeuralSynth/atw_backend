"""
ASGI config for ATW Backend project.

Supports both HTTP and WebSocket protocols for real-time GPS tracking.
"""

import os

from django.core.asgi import get_asgi_application

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django ASGI application early (before importing Channels)
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402

# Import Channels components after Django setup
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402

import trips.routing  # noqa: E402

# ASGI application with WebSocket support
application = ProtocolTypeRouter(
    {
        # HTTP requests handled by Django
        "http": django_asgi_app,
        # WebSocket requests handled by Channels
        "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(trips.routing.websocket_urlpatterns))),
    }
)
