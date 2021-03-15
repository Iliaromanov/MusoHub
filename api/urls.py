from django.urls import path
from .views import main

urlpatterns = [
    path('home', main) # for home route request call main function from views
]