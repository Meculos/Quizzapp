from django.shortcuts import render, redirect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import (IsAuthenticated, IsAdminUser, AllowAny)
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, GameRoom, Player, GameState
from .serializers import GameRoomSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import status, generics, viewsets

# Create your views here.

# rest framework views.....
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        email = request.data.get("email", "").strip()
        password1 = request.data.get("password1", "")
        password2 = request.data.get("password2", "")

        if not username or not email or not password1 or not password2:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if password1 != password2:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password1)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(username=username, email=email)
        user.set_password(password1)
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "User successfully created",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        }, status=status.HTTP_201_CREATED)
    
class ListCreateGameRoom(viewsets.ModelViewSet):
    serializer_class = GameRoomSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return GameRoom.objects.filter(is_active=True)

    def perform_create(self, serializer):
        """Auto-assign host when a room is created and add them as a player"""
        if not self.request.user or self.request.user.is_anonymous:
            raise serializers.ValidationError({"error": "User must be authenticated."})

        game_room = serializer.save(host=self.request.user)

        # Create Player instance for the host
        Player.objects.create(user=self.request.user, game=game_room, is_ready=False)

        # Add host to the players field in GameRoom
        game_room.players.add(self.request.user)

    
# django views.......
def register(request):
    return render(request, "quiz_app/register.html")

def login(request):
    return render(request, "quiz_app/login.html")

def index(request):
    return render(request, "quiz_app/index.html")

def gameroom(request):
    return render(request, "quiz_app/gameroom.html")

def join_game_room(request, room_code):
    """Handles players joining a game room and redirects them to the lobby"""
    game_room = get_object_or_404(GameRoom, room_code=room_code)

    # Add user to game if not already in it
    if not Player.objects.filter(user=request.user, game=game_room).exists():
        Player.objects.create(user=request.user, game=game_room)
        game_room.players.add(request.user)

    return redirect(f"/quiz_app/game_room/{room_code}/lobby/")

def game_lobby(request, room_code):
    """Render the lobby page"""
    game_room = get_object_or_404(GameRoom, room_code=room_code)
    is_host = request.user == game_room.host

    return render(request, "quiz_app/lobby.html", {
        "room_code": room_code,
        "is_host": is_host
    })