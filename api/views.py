from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView # generic api view
from rest_framework.response import Response

from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room


# Create your views here.

# Use .CreateAPIView if need want POST to be enabled
# .ListAPIView only allows GET requests
class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class GetRoom(APIView): 
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'code'

    def get(self, request, format=None):
        code = request.GET.get(self.lookup_url_kwarg)

        if code != None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                data = RoomSerializer(room_result[0]).data
                # Is true iff current user session key is equal to host of room in the db
                data['is_host'] = self.request.session.session_key == room_result[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'Bad Request': 'Room parameter not found in request'}, status=status.HTTP_400_BAD_REQUEST)


class JoinRoom(APIView):
    lookup_url_kwarg = 'code'

    def post(self, request, format=None):
        # Check if current user has a session and if not then create one
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                self.request.session['room_code'] = code # save the room code in session
                return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)
            return Response({'Bad Request': 'Invalid Room Code'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Bad Request': 'Did not find a code key'}, status=status.HTTP_400_BAD_REQUEST)


class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        # Check if current user has a session and if not then create one
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)

        # If fields specified in serializer class are present
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key

            # Check if there are any existing rooms in the db with current host
            queryset = Room.objects.filter(host=host)

            # If host already has a room, update its fields
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])

                self.request.session['room_code'] = room.code # save the room code in session
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            # Otherwise, create a new room with the specified fields
            else:
                room = Room(host=host, guest_can_pause = guest_can_pause, votes_to_skip = votes_to_skip)
                room.save()

                self.request.session['room_code'] = room.code # save the room code in session
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)

