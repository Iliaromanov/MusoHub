from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from requests import Request, post

from .util import update_or_create_user_tokens
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

    # This actually sends a requests and generates and saves a response
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh.token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    # Ensure current user is in session
    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('frontend:')





    

