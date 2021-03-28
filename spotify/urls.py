from django.urls import path
from .views import *

urlpatterns = [
    # any url thats not api or admin will be directed to frontend directory
    path('get-auth-url', AuthURL.as_view()),
    path('redirect', spotify_callback),
    path('is-authenticated', IsAuthenticated.as_view()),
    path('current-song', CurrentSong.as_view()),
    path('play', PlaySong.as_view()),
    path('pause', PauseSong.as_view())
]