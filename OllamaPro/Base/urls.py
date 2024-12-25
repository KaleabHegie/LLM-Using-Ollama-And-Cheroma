from django.urls import path, include
from .views import ask_questions , chat


urlpatterns = [
    path('<int:id>', ask_questions , name='ask_questions'),
    path('chat/<int:id>' , chat , name='chat'),
]