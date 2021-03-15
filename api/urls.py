from django.urls import path
from .views import RoomView

urlpatterns = [
    path('room', RoomView.as_view()) # for home route request call main function from views
]