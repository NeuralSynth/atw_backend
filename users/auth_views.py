from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint - returns authentication token
    
    POST /api/v1/auth/login/
    Body: {"username": "admin", "password": "admin123"}
    Returns: {"token": "abc123...", "user_id": 1, "username": "admin"}
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if not user:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Get or create token
    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": getattr(user, "role", ""),
        }
    )


@api_view(["POST"])
def logout(request):
    """
    Logout endpoint - deletes authentication token
    
    POST /api/v1/auth/logout/
    Headers: Authorization: Token abc123...
    """
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def user_profile(request):
    """
    Get current user profile
    
    GET /api/v1/auth/profile/
    Headers: Authorization: Token abc123...
    """
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": getattr(user, "role", ""),
            "status": getattr(user, "status", ""),
        }
    )
