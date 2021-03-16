from django.urls import path
from .views import RoomView, CreateRoomView, GetRoom

urlpatterns = [
    path('room', RoomView.as_view()), # for home route request call main function from views
    path('create-room', CreateRoomView.as_view()),
    path('get-room', GetRoom.as_view())
]