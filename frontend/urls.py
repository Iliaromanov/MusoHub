from django.urls import path
from .views import index

urlpatterns = [
    # any url thats not api or admin will be directed to frontend directory
    path('', index),
    path('join', index),
    path('create', index)
]
