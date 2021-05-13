from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, status
from .models import Room
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer

from rest_framework.views import APIView
from rest_framework.response import Response

class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        # If a session doesn't exist, create one. 
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        # if the serializer is valid, assign values to variables (guest_can_pause, votes_to_skip, host)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            # Before creating a room, check to see if host already has a room:
            queryset = Room.objects.filter(host=host)
            # If room exists, update it.
            if queryset.exists():
                room = queryset.first()
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip']) # to update, room.save(update_fields=[<list of fields that need to be updated>])
                # registers the room user is in
                self.request.session['in_room'] = room.code
                # We need to serialize UPDATED room before sending it back to the web page
                serialized_room_json = RoomSerializer(room).data
                status_code = status.HTTP_201_CREATED
                return Response(serialized_room_json, status=status_code)
            else: # Otherwise if no room exists, create one:
                room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip)
                room.save()
                # registers the room user is in
                self.request.session['in_room'] = room.code
                # We need to serialize the NEWLY CREATED room before sending it back to the web page
                serialized_room_json = RoomSerializer(room).data
                status_code = status.HTTP_200_OK
                return Response(serialized_room_json, status=status_code)
        else: # if the serializer is not valid, send a bad resquest response
            bad_request_response_json = {'Bad Request': 'Invalid data...'}
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(bad_request_response_json, status=status_code)

class GetRoomView(APIView):
    serializer_class = RoomSerializer

    def get(self, request, format=None):
        code = request.query_params.get('code')
        
        if code != None:
            room = Room.objects.filter(code=code).first()
            if room:
                data = RoomSerializer(room).data
                data['is_host'] = self.request.session.session_key == room.host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad Request': 'Code parameter not found'}, status=status.HTTP_400_BAD_REQUEST)

class JoinRoomView(APIView):
    serializer_class = RoomSerializer

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code = request.data.get('code')
        queryset = Room.objects.filter(code=code)

        if len(code) > 0:

            if queryset.exists():

                room = queryset.first()

                self.request.session['in_room'] = code # registers what room user is in

                serialized_room_json = RoomSerializer(room).data
                status_code = status.HTTP_200_OK
                return Response(serialized_room_json, status=status_code)
                
            response = {'error': 'Invalid room code'}
            status_code = status.HTTP_404_NOT_FOUND
            return Response(response, status=status_code)

        response = {'error': 'Enter room code'}
        status_code = status.HTTP_400_BAD_REQUEST
        return Response(response, status=status_code)  

class UserInRoom(APIView):
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            
        data = {
            'code': self.request.session.get('in_room')
        }
        return JsonResponse(data, status=status.HTTP_200_OK)

class LeaveRoom(APIView):
    def post(self, request, format=None):
        if 'in_room' in self.request.session:
            code = self.request.session.pop('in_room')
            queryset = Room.objects.filter(code=code)

            if queryset.exists():
                room = queryset.first()
                if self.request.session.session_key == room.host:
                    room.delete()
                    return Response({"Message": "Success - user left room and room deleted"}, status=status.HTTP_200_OK)
            return Response({"Message": "Success - user has left the room"}, status=status.HTTP_200_OK)
            
class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer

    def patch(self, request, format=None):

        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = UpdateRoomSerializer(data=request.data)

        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            queryset = Room.objects.filter(code=code)

            if queryset.exists():
                room = queryset.first()

                if self.request.session.session_key == room.host:
                    room.guest_can_pause = guest_can_pause
                    room.votes_to_skip = votes_to_skip
                    room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

                return Response({"Error": "Only host can delete room"}, status=status.HTTP_403_FORBIDDEN)
            return Response({"Error" : "Room does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
