from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from requests import Request, post
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta

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