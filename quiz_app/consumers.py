import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import GameRoom, Player


class GameLobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"game_lobby_{self.room_code}"

        # Join the WebSocket room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send updated lobby info
        await self.send_lobby_data()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "ready_up":
            player_id = data.get("player_id")
            await self.set_player_ready(player_id)

        elif action == "start_game":
            await self.start_game()

        # Send updated lobby info to all clients
        await self.send_lobby_data()

    async def send_lobby_data(self):
        """Fetch and send the latest game lobby data to all clients."""
        game_room = await self.get_game_room()

        if not game_room:
            return

        players = await self.get_players(game_room)
        all_ready = all(p["is_ready"] for p in players) if players else False

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_lobby",
                "players": players,
                "all_ready": all_ready,
            }
        )

    async def broadcast_lobby(self, event):
        """Send lobby updates to all connected clients."""
        await self.send(text_data=json.dumps(event))

    # ✅ Async Database Helper Methods
    @sync_to_async
    def get_game_room(self):
        """Fetch the game room from the database."""
        return GameRoom.objects.filter(room_code=self.room_code).first()

    @sync_to_async
    def get_players(self, game_room):
        """Get all players in the game room."""
        return [
            {"id": p.id, "username": p.user.username, "is_ready": p.is_ready}
            for p in Player.objects.filter(game=game_room)
        ]

    @sync_to_async
    def set_player_ready(self, player_id):
        """Mark a player as ready."""
        player = Player.objects.filter(id=player_id).first()
        if player:
            player.is_ready = True
            player.save()

    @sync_to_async
    def start_game(self):
        """Start the game if all players are ready."""
        game_room = GameRoom.objects.filter(room_code=self.room_code).first()
        if game_room:
            players = Player.objects.filter(game=game_room)
            if all(player.is_ready for player in players):  # Ensure all are ready
                game_room.is_active = False  # Mark game as started
                game_room.save()
