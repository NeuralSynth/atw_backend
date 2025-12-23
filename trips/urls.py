from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"trips", views.TripViewSet)
router.register(r"messages", views.ChatMessageViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
