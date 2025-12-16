from rest_framework import viewsets, permissions
from .models import EMSReport
from .serializers import EMSReportSerializer

class EMSReportViewSet(viewsets.ModelViewSet):
    queryset = EMSReport.objects.all()
    serializer_class = EMSReportSerializer
    permission_classes = [permissions.IsAuthenticated]
