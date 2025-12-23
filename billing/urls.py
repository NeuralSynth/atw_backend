from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"invoices", views.InvoiceViewSet)
router.register(r"contracts", views.ContractViewSet)
router.register(r"settings", views.SystemSettingsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
