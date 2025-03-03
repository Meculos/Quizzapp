from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # jwt paths
    path('api/login_token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # rest framework paths
    path('register/', views.RegisterView.as_view()),

    # django paths
    path('register_page/', views.register, name='register_view'),
    path('login_page/', views.login, name='login_view'),
    path('', views.index, name='homepage'),
    path('game_room/<uuid:room_code>/', views.join_game_room, name="join_game_room"),
    path('game_room/<str:room_code>/lobby/', views.game_lobby, name="game_lobby"),
    path("game_room/", views.gameroom, name="game_room"),
]

router = DefaultRouter()
router.register('api/game_room', views.ListCreateGameRoom, basename='game-room')
urlpatterns += router.urls