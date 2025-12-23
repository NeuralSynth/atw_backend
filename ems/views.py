from rest_framework import permissions, viewsets

from .models import EMSReport
from .serializers import EMSReportSerializer


class EMSReportViewSet(viewsets.ModelViewSet):
    queryset = EMSReport.objects.all()
    serializer_class = EMSReportSerializer
    permission_classes = [permissions.IsAuthenticated]
