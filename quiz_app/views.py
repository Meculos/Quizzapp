from django.shortcuts import render, redirect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import (IsAuthenticated, IsAdminUser, AllowAny)
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, GameRoom, Player, GameState, Question
from .serializers import GameRoomSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers
import random
from rest_framework import status, generics, viewsets
import datetime


from django.http import JsonResponse

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

        User.objects.create_user(username=username, email=email, password=password1)  # ✅ Fix: create_user()
        
        return Response({
            "message": "User successfully created",
        }, status=status.HTTP_201_CREATED)

class LoginApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user) 
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            response = Response({"message": "User logged in successfully",}, status=status.HTTP_201_CREATED)

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True, 
                samesite="None"
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                samesite="None"
            )
            return response
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutApiView(APIView):
    def post(self, request):
        logout(request)
        response = JsonResponse({"message": "Logged out successfully"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
    
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "No refresh token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_access_token = str(RefreshToken(refresh_token).access_token)
            response = Response({"message": "Token refreshed"}, staus=status.HTTP_200_OK)
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                samesite="None"
            )
            return response
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
    
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

    
# django views......
def register(request):
    return render(request, "quiz_app/register.html")

def login_user(request):
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

def game_area(request, room_code):
    return render(request, "quiz_app/game_area.html", {
        "room_code": room_code,
    })

def game_results(request, room_code):
    return render(request, "quiz_app/game_results.html", {
        "room_code": room_code,
    })

def single_play_category(request):
    categories = [{'value': choice[0], 'label': choice[1]} for choice in Question.CATEGORY_CHOICES]

    return render(request, "quiz_app/single_play_category.html", {
        "categories": categories,
    })

def single_play_game(request, category):
    # Check if game already exists in session
    if 'game_questions' in request.session:
        prepared_questions = request.session['game_questions']
    else:
        # Prepare new questions
        questions = list(Question.objects.filter(category=category))
        random_questions = random.sample(questions, min(len(questions), 20))

        prepared_questions = []
        for question in random_questions:
            answers = question.wrong_answers + [question.correct_answer]
            random.shuffle(answers)

            prepared_answers = []
            for answer in answers:
                prepared_answers.append({
                    "text": answer,
                    "is_correct": answer == question.correct_answer
                })

            prepared_questions.append({
                "question_text": question.question_text,
                "answers": prepared_answers,
            })

        # Store in session!
        request.session['game_questions'] = prepared_questions

    return render(request, "quiz_app/single_play_game.html", {
        "questions": prepared_questions
    })

def end_game(request):
    if 'game_questions' in request.session:
        del request.session['game_questions']
    return JsonResponse({'message': 'Game ended'})

def results(request):
    return render(request, "quiz_app/results.html")