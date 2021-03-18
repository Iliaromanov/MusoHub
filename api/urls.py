from django.urls import path
from .views import JoinRoom, RoomView, CreateRoomView, GetRoom, UserInRoom

urlpatterns = [
    path('room', RoomView.as_view()), # for home route request call main function from views
    path('create-room', CreateRoomView.as_view()),
    path('get-room', GetRoom.as_view()),
    path('join-room', JoinRoom.as_view()),
    path('user-in-room', UserInRoom.as_view())
]