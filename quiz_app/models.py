from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.

class GameRoom(models.Model):
    """Handles multiplayer game sessions"""
    room_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hosted_games")
    players = models.ManyToManyField(User, through="Player", related_name="games")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GameRoom {self.room_code} created by {self.host.username}" 

class Player(models.Model):
    """Tracks player stats within a game room"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    is_ready = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user.username} in {self.game.room_code}" 

class Question(models.Model):
    """Stores trivia questions"""
    CATEGORY_CHOICES = [
        ("history", "History"),
        ("geography", "Geography"),
        ("sports", "Sports"),
        ("random", "Random"),
        ("literature", "Literature"),
        ("video_games", "Video Games"),
        ("movies", "Movies"),
        ("music", "Music"),
        ("anime", "Anime"),
        ("mythology", "Mythology"),
        ("nature", "Nature"),
        ("comics", "Comics"),
        ("cartoons", "Cartoons")
    ]
    
    question_text = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    correct_answer = models.CharField(max_length=255)
    wrong_answers = models.JSONField()
    
    def __str__(self):
        return self.question_text

class GameState(models.Model):
    """Tracks game progress, including scores and current question"""
    game = models.OneToOneField(GameRoom, on_delete=models.CASCADE, related_name="state")
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    question_index = models.IntegerField(default=0)
    is_over = models.BooleanField(default=False)
    
    def __str__(self):
        return f"GameState for {self.game.room_code}"
