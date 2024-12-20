from django.urls import path, include
from .views import *


urlpatterns = [
    path('', ask_questions , name='ask_questions'),
    path('chat/' , chat , name='chat'),
]