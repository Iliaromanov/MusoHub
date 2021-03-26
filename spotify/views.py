from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from requests import Request, post

from api.models import Room
# Star means import everything defined in .util
from .util import *
from .credentials import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET


# View to return a url that we will give to the frontend to request
#   authorization from end user to use their spotify
class AuthURL(APIView):
    def get(self, request, format=None):
        scopes = """
                 user-read-playback-state 
                 user-modify-playback-state 
                 user-read-currently-playing
                 """
        
        # response_type = code because we want to get the code from Spotify that
        #  gives us access to the tokens we can use to get access to users account
        # This generates a url that we will give to the frontend to make request
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url

        return Response({'url': url}, status.HTTP_200_OK)


# Callback function to get the tokens using the code that we obtain using
#  the above views url. 
#  (Step 2: in Spotify API flowchart; the part after user authorizes access)
def spotify_callback(request, fromat=None):
    code = request.GET.get('code')
    # can be used to display error if we get one from the response
    error = request.GET.get('error')

    # This actually sends a request and generates and saves a response
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    # Ensure current user is in session
    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token)

    # To redirect to a page in a different app, do {app name}:{page}
    # eg. frontend:room
    # In this case we just want to redirect to the homepage so nothing after :
    return redirect('frontend:')


# Endpoint to return json response 
class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        #print("HERE-------------------------------------------")
        #print(is_authenticated)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)


# Gets information about a song
class CurrentSong(APIView):
    def get(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        host = room.host
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(host, endpoint)
        print(response)

        return Response(response, status=status.HTTP_200_OK)


