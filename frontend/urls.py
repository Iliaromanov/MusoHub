from django.urls import path
from .views import index

# So that redirect inside of spotify/views.py works
app_name = 'frontend'

urlpatterns = [
    # any url thats not api or admin will be directed to frontend directory
    path('', index, name=''),
    path('join', index),
    path('create', index),
    path('room/<str:roomCode>', index)
]
