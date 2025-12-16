from rest_framework import serializers
from .models import EMSReport

class EMSReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMSReport
        fields = '__all__'
