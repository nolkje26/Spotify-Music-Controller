from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from requests import Request, post, get
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from api.models import Room

'''
Request authorization to access data using: client_id, response_type, redirect_uri and scope
'''
class AuthURL(APIView):
    def get(self, request, format=None):
        method = 'GET'
        endpoint = 'https://accounts.spotify.com/authorize'
        params = {
            'scope': 'user-read-playback-state user-modify-playback-state user-read-currently-playing',
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }

        url = Request(method, endpoint, params=params).prepare().url
        
        return Response({'url': url}, status=status.HTTP_200_OK)

def get_user_tokens(session_key):
    user_tokens = SpotifyToken.objects.filter(user=session_key)
    if user_tokens.exists():
        return user_tokens.first()
    return None

def update_or_create_tokens(session_key, access_token, token_type, refresh_token, expires_in):
    tokens = get_user_tokens(session_key)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else: 
        tokens = SpotifyToken(user=session_key, access_token=access_token, token_type=token_type, refresh_token=refresh_token, expires_in=expires_in)
        tokens.save()

def spotify_callback(request, format=None):
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    endpoint = 'https://accounts.spotify.com/api/token'

    request_body_params = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = post(endpoint, data=request_body_params).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_tokens(request.session.session_key, access_token, token_type, refresh_token, expires_in)

    return redirect('frontend:')

def refresh_spotify_token(session_key):
    tokens = get_user_tokens(session_key)
    refresh_token = tokens.refresh_token

    endpoint = 'https://accounts.spotify.com/api/token'
    request_body_params = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = post(endpoint, data=request_body_params).json()
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    refresh_token = response.get('refresh_token')

    update_or_create_tokens(session_key, access_token, token_type, refresh_token, expires_in)

def is_spotify_authenticated(session_key):
    tokens = get_user_tokens(session_key)
    if tokens:
        if tokens.expires_in <= timezone.now():
            refresh_spotify_token(session_key)
        return True
    return False

class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)

class CurrentSong(APIView):
    def get(self, request, format=None):
        # Only the host's session key will be liked to the spotify account. So if the client requesting 
        # to the Spotify API is not the host, then we first need to figure out what room they are, and then
        # grab the host's session key

        room_code = self.request.session.get('in_room') 
        rooms = Room.objects.filter(code=room_code)

        if rooms.exists():
            room = rooms.first()
        else:
            return Response({'Error': 'Room Not Found'}, status=status.HTTP_404_NOT_FOUND)
        host = room.host # this is the session key
        # Documentation: https://developer.spotify.com/documentation/web-api/reference/#endpoint-currently-playing
        endpoint = "https://api.spotify.com/v1/me/player/currently-playing"
        tokens = get_user_tokens(host)
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + tokens.access_token}
        response = get(endpoint, {}, headers=headers)
        
        if response.reason and response.reason != 'OK':
            if response.reason == 'No Content':
                return Response({'Error': " Play something on Spotify."}, status=status.HTTP_204_NO_CONTENT)
            elif response.reason == 'Unauthorized': 
                return Response({'Error': " Please sign in."}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'Error': response.reason}, status=status.HTTP_400_BAD_REQUEST)

        response = response.json()

        if 'error' in response :
                return Response({ 'Error' : response.get('error').get('message')}, status=response.get('error').get('status'))

        if 'item' not in response:
            return Response({'Error': 'Issue with Request'}, status=status.HTTP_204_NO_CONTENT)

        item = response.get('item')
        title = item.get('name')
        song_id = item.get('id')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[1].get('url')
        is_playing = response.get('is_playing')

        artists_string = ''

        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artists_string += ', '
            name = artist.get('name')
            artists_string += name

        song = {
            'title': title,
            'id': song_id,
            'artist': artists_string,
            'duration': duration,
            'progress': progress,
            'img_url': album_cover,
            'is_playing': is_playing,
            'votes': 0
        }
        
        return Response(song, status=status.HTTP_200_OK)

