"""
Health check endpoints for Kubernetes liveness and readiness probes.
"""

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check endpoint for Kubernetes liveness probe.

    GET /api/v1/health/

    Returns 200 OK if the application is running.
    This is a simple ping to verify the process is alive.
    """
    return Response(
        {
            "status": "healthy",
            "service": "atw-backend",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check endpoint for Kubernetes readiness probe.

    GET /api/v1/ready/

    Checks critical dependencies:
    - Database connectivity
    - Cache (Redis) connectivity

    Returns 200 OK if all dependencies are available.
    Returns 503 Service Unavailable if any dependency is down.
    """
    checks = {
        "database": False,
        "cache": False,
    }

    errors = []

    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks["database"] = True
    except Exception as e:
        errors.append(f"Database error: {str(e)}")

    # Check cache (Redis) connectivity
    try:
        cache.set("health_check", "ok", timeout=10)
        if cache.get("health_check") == "ok":
            checks["cache"] = True
        else:
            errors.append("Cache read/write failed")
    except Exception as e:
        errors.append(f"Cache error: {str(e)}")

    # Determine overall readiness
    is_ready = all(checks.values())

    response_data = {
        "status": "ready" if is_ready else "not_ready",
        "service": "atw-backend",
        "checks": checks,
    }

    if errors:
        response_data["errors"] = errors

    return Response(
        response_data,
        status=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
    )
