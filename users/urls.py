from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import auth_views, views

router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"companies", views.CompanyViewSet)

urlpatterns = [
    # Authentication endpoints
    path("auth/login/", auth_views.login, name="login"),
    path("auth/logout/", auth_views.logout, name="logout"),
    path("auth/profile/", auth_views.user_profile, name="profile"),
    # ViewSet routes
    path("", include(router.urls)),
]
