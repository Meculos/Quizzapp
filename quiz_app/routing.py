from django.urls import path
from .consumers import GameLobbyConsumer, GameAreaConsumer, GameResultConsumer

websocket_urlpatterns = [
    path("ws/game_lobby/<str:room_code>/", GameLobbyConsumer.as_asgi()),
    path("ws/game_area/<str:room_code>/", GameAreaConsumer.as_asgi()),
    path("ws/game_results/<str:room_code>/", GameResultConsumer.as_asgi())
]