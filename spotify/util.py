# Helper functions for views.py
import requests
from spotify.credentials import CLIENT_ID, CLIENT_SECRET
from django.utils import timezone
from datetime import timedelta
from requests import post

from .models import SpotifyTokens

# Searches SpotifyToken table for current user and returns their token info
def get_user_tokens(session_id):
    user_tokens = SpotifyTokens.objects.filter(user=session_id)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None


# Updates a given users tokens in the SpotifyToken table
def update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(session_id)
    # Save the time at which the access token is going to expire
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyTokens(user=session_id, 
                              access_token=access_token, 
                              refresh_token=refresh_token,
                              token_type=token_type,
                              expires_in=expires_in)
        tokens.save()


# Returns true if user is has authenticated their spotify
def is_spotify_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    if tokens:
        expiry = tokens.expires_in
        # If tokens expired, then refresh token
        if expiry <= timezone.now():
            refresh_spotify_token(session_id)

        return True
    
    return False

# Refreshes a users spotify token
def refresh_spotify_token(session_id):
    refresh_token = get_user_tokens(session_id).refresh_token

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    #print("THIS IS EXPIRES IN =========" + expires_in)
    refresh_token = response.get('refresh_token')

    update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token)
