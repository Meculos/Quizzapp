from django.contrib import admin
from .models import Question, GameRoom, GameState, Player

# Register your models here.
admin.site.register(Question)
admin.site.register(GameRoom)
admin.site.register(GameState)
admin.site.register(Player)
