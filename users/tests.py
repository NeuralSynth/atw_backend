"""
Tests for user authentication and management - Fixed to match actual models.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from users.models import Company, User


class AuthenticationTestCase(TestCase):
    """Test authentication endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_login_with_valid_credentials(self):
        """Test login with valid username and password."""
        url = reverse("login")
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials returns 401."""
        url = reverse("login")
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_login_without_username(self):
        """Test login without username returns 400."""
        url = reverse("login")
        data = {"password": "testpass123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """Test logout deletes user token."""
        # Create token for user
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        url = reverse("logout")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify token was deleted
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_user_profile_authenticated(self):
        """Test getting user profile with valid token."""
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        url = reverse("profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_user_profile_unauthenticated(self):
        """Test getting user profile without token returns 401."""
        url = reverse("profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserViewSetTestCase(TestCase):
    """Test user management endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            is_staff=True,
        )
        self.token = Token.objects.create(user=self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_list_users(self):
        """Test listing all users."""
        url = reverse("user-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_user(self):
        """Test creating a new user."""
        url = reverse("user-list")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_get_user_detail(self):
        """Test retrieving user details."""
        url = reverse("user-detail", kwargs={"pk": self.admin_user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "admin")


class CompanyTestCase(TestCase):
    """Test company management."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_company(self):
        """Test creating a company."""
        url = reverse("company-list")
        data = {
            "company_name": "Test Company",
            "company_type": Company.Type.CLIENT,
            "phone_number": "+1234567890",
            "email": "company@example.com",
            "address": "123 Test St",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Company.objects.filter(company_name="Test Company").exists())

    def test_list_companies(self):
        """Test listing companies."""
        Company.objects.create(
            company_name="Company A",
            company_type=Company.Type.CLIENT,
            phone_number="+1111111111",
            email="a@example.com",
        )
        Company.objects.create(
            company_name="Company B",
            company_type=Company.Type.VENDOR,
            phone_number="+2222222222",
            email="b@example.com",
        )

        url = reverse("company-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
