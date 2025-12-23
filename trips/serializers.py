from rest_framework import serializers

from .models import ChatMessage, Trip


class TripSerializer(serializers.ModelSerializer):
    total_distance = serializers.ReadOnlyField()

    class Meta:
        model = Trip
        fields = "__all__"


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"
