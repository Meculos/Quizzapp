from rest_framework import serializers

from .models import GameRoom, GameState, User, Player, Question

class GameRoomSerializer(serializers.ModelSerializer):
    host_username = serializers.CharField(source="host.username", read_only=True)
    class Meta:
        model = GameRoom
        fields = ["id", "room_code", "host", "players", "is_active", "created_at", "host_username"]
        read_only_fields = ["id", "room_code", "created_at", "host", "host_username"]

class GameStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameState
        fields = ["id", "game", "current_question", "question_index", "is_over"]
        read_only_fields = ["id"]

class PlayerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)  # Include username
    
    class Meta:
        model = Player
        fields = ["id", "user", "username", "game", "score", "is_ready"]
        read_only_fields = ["id", "username"]

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "category", "question_text", "correct_answer", "wrong_answers", "created_at"]
        read_only_fields = ["id"]