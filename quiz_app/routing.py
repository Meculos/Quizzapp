from django.urls import path
from .consumers import GameLobbyConsumer

websocket_urlpatterns = [
    path("ws/game_lobby/<str:room_code>/", GameLobbyConsumer.as_asgi()),
]