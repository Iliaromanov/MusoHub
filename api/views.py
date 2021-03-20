from django.http.response import JsonResponse
from django.shortcuts import render
from rest_framework import generics, serializers, status
from rest_framework.fields import SerializerMethodField
from rest_framework.views import APIView # generic api view
from rest_framework.response import Response
from django.http import JsonResponse

from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
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


class UserInRoom(APIView):
    def get(self, request, format=None):
        # Ensure user in session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        # Save and return the code of the room in which the user is in if it exists
        room = self.request.session.get('room_code')
        data = {
            'code': room
        }
        # JsonResponse serializes a Python dictionary and returns it in json format
        return JsonResponse(data=data, status=status.HTTP_200_OK)


class LeaveRoom(APIView):
    def post(self, request, format=None):
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code')
            host_id = self.request.session.session_key

            # Delete room for which the user leaving was the host
            room_results = Room.objects.filter(host=host_id)
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()
            
        return Response({'Message': 'Success'}, status=status.HTTP_200_OK)



'''
**This  view assumes each host only has one room**

-Could add functionality for host to run multiple rooms and choose which one to edit here
-Could add functionality for host to give someone else hosting priveledges
'''
class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer

    # patch is used when updating something on the server
    # (get -> getting something; post -> creating something on the server)
    def patch(self, request, format=None):
        # Ensure session exists for current user
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            queryset = Room.objects.filter(code=code)
            if queryset.exists():

                room = queryset[0]

                user_id = self.request.session.session_key

                if user_id == room.host:
                    room.guest_can_pause = guest_can_pause
                    room.votes_to_skip = votes_to_skip
                    room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

                return Response({'msg': 'You are not the host of this room'}, status=status.HTTP_403_FORBIDDEN)
            
            return Response({'msg': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)
