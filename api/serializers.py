# converts tables from database into JSON format

from rest_framework import serializers
from .models import Room


# Handles GET requests (serializes all info about room)
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'code', 'host', 'guest_can_pause', 'votes_to_skip', 'created_at')


# Serializer to handle POST requests for creating rooms
class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        # The fields we need from the POST request
        fields = ('guest_can_pause', 'votes_to_skip') # dont need host since thats a session key


class UpdateRoomSerializer(serializers.ModelSerializer):
    # Redefining code field from model so that it doesn't have to be unique
    code = serializers.CharField(validators=[])
    
    class Meta:
        model = Room
        fields = ('code', 'guest_can_pause', 'votes_to_skip')
