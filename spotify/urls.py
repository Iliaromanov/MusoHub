from django.urls import path
from .views import AuthURL

urlpatterns = [
    # any url thats not api or admin will be directed to frontend directory
    path('get-auth-url', AuthURL.as_view()),
]