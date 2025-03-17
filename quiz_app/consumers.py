import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from .models import GameRoom, Player, Question, GameState, PlayerGameState
import random, asyncio
from datetime import datetime, timedelta


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

    async def start_game(self):
        """Start the game if all players are ready and notify clients."""
        
        # Fetch game room safely
        game_room = await sync_to_async(lambda: GameRoom.objects.filter(room_code=self.room_code).first())()
        
        if game_room:
            # Fetch all players safely
            players = await sync_to_async(lambda: list(Player.objects.filter(game=game_room)))()

            # Ensure all players are ready
            if all(player.is_ready for player in players):  
                # Mark game as started (must be inside sync_to_async)
                await sync_to_async(lambda: setattr(game_room, 'is_active', False))()
                await sync_to_async(game_room.save)()

                # Send game start message to all players
                channel_layer = get_channel_layer()
                await channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_started"
                    }
                )

    async def game_started(self, event):
        """Notify all clients to redirect when the game starts."""
        await self.send(text_data=json.dumps({
            "type": "start_game"
        }))

class GameAreaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"game_area_{self.room_code}"

        # Fetch game room once on connection
        self.game_room = await database_sync_to_async(GameRoom.objects.get)(room_code=self.room_code)

        # Join the WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Start the game
        await self.start_game()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def start_game(self):
        """Starts the game by selecting a category and fetching questions."""
        categories = [choice[0] for choice in Question.CATEGORY_CHOICES]
        selected_category = random.choice(categories)

        questions = await database_sync_to_async(
            lambda: list(Question.objects.filter(category=selected_category).order_by("?")[:20])
        )()

        # Fetch or create the game state
        game_state, created = await database_sync_to_async(GameState.objects.get_or_create)(game=self.game_room)

        if not created and game_state.end_time:
            return

        game_state.questions = [q.id for q in questions]  # Store question IDs
        game_state.end_time = datetime.now() + timedelta(minutes=2)

        await database_sync_to_async(game_state.save)()  # Save the updated GameState

        question_list = [
            {
                "id": q.id,
                "question_text": q.question_text,
                "answers": random.sample(q.wrong_answers + [q.correct_answer], len(q.wrong_answers) + 1),
                "correct_answer": q.correct_answer,
            }
            for q in questions
        ]

        # Store game state
        self.game_data = {
            "category": selected_category,
            "questions": question_list,
            "end_time": game_state.end_time.isoformat(),
        }

        # Send data to all players
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_game_data",
                "game_data": self.game_data,
            }
        )

    async def send_game_data(self, event):
        """Sends game data to all players."""
        await self.send(text_data=json.dumps({
            "type": "game_start",
            "game_data": event["game_data"],
        }))

    async def receive(self, text_data):
        """Handles user answers."""
        data = json.loads(text_data)

        if data["type"] == "submit_answer":
            question_id = data["question_id"]
            selected_answer = data["answer"]
            player = self.scope["user"]  # Assuming authenticated users

            # Get the game state and player state
            game_state, _ = await database_sync_to_async(GameState.objects.get_or_create)(game=self.game_room)
            player_state, _ = await database_sync_to_async(PlayerGameState.objects.get_or_create)(
                game_state=game_state, player=player
            )

            question_ids = await database_sync_to_async(lambda: game_state.questions)()
            questions = await database_sync_to_async(lambda: list(Question.objects.filter(id__in=question_ids)))()


            # Find the correct answer
            correct_answer = None
            for q in questions:
                if q.id == question_id:  # Now q is a Question object, so this works
                    correct_answer = q.correct_answer
                    break

            if correct_answer is None:
                return  # Invalid question ID

            # Submit the answer and update score
            await database_sync_to_async(player_state.submit_answer)(question_id, selected_answer, correct_answer)

            # Broadcast updated scores
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "update_scores",
                }
            )

        elif data["type"] == "end_game":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_end",
                }
            )

    async def update_scores(self, event):
        # Fetch game state
        game_state = await database_sync_to_async(GameState.objects.get)(game=self.game_room)

        # Fetch all player states
        player_states = await database_sync_to_async(lambda: list(PlayerGameState.objects.filter(game_state=game_state)))()

        # Fetch player usernames asynchronously
        async def get_player_data(state):
            player = await database_sync_to_async(lambda: state.player)()  # Fetch player
            return {"username": player.username, "score": state.score}  # Now access safely

        scores = await asyncio.gather(*(get_player_data(state) for state in player_states))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_scores",
                "scores": scores,
            }
        )

    async def send_scores(self, event):
        await self.send(text_data=json.dumps({
            "type": "update_scores",
            "scores": event["scores"],
        }))

    async def game_end(self, event):
        """Sends game end signal to all clients."""
        await self.send(text_data=json.dumps({
            "type": "game_end",
        }))

class GameResultConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"game_results_{self.room_code}"

        # Join the WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Fetch game results
        await self.game_results()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def game_results(self):
        """Fetch and send game results"""
        gameroom = await database_sync_to_async(GameRoom.objects.get)(room_code=self.room_code)
        gamestate = await database_sync_to_async(GameState.objects.get)(game=gameroom)

        # Ensure safe query execution
        player_states = await database_sync_to_async(lambda: list(
            PlayerGameState.objects.filter(game_state=gamestate).order_by("-score")
        ))()

        async def get_player_score(state):
            player = await database_sync_to_async(lambda: state.player)()  # Fetch player safely
            return {"username": player.username, "score": state.score}  # Return player data

        # Fetch all player scores concurrently
        results = await asyncio.gather(*(get_player_score(state) for state in player_states))

        # Send results to the WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_result_data",
                "results": results,
            }
        )
        
    async def send_result_data(self, event):
        """Send game results to all players"""
        await self.send(text_data=json.dumps({
            "type": "display_results",
            "results": event["results"],
        }))

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        data = json.loads(text_data)

        if data['type'] == "finish_game":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "finish_game"
                }
            )

    async def finish_game(self, event):
        """Notify all clients that the game is finished"""
        await self.send(text_data=json.dumps({
            "type": "finish_game"
        }))

            
