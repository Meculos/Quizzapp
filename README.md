# Quiz App

A real-time multiplayer quiz game built with Django, Django Rest Framework (DRF), Django Channels, WebSockets, and JWT authentication. Players can create game rooms, invite others, and compete in trivia challenges.

## Features
- **User Authentication** (JWT-based login/logout)
- **Game Room Creation** (with automatic host assignment)
- **Real-time Gameplay** using WebSockets
- **Multiplayer Trivia System**
- **Leaderboard & Scores Tracking**
- **REST API for Game Management**
- **WebSocket-based Player Communication**

## Tech Stack
- **Backend:** Django, Django Rest Framework, Django Channels, Redis
- **Frontend:** JavaScript (fetch API for API requests, WebSockets for real-time updates)
- **Database:** PostgreSQL (or SQLite for local development)
- **Authentication:** JWT (Django SimpleJWT)
- **WebSockets:** Django Channels + Redis

---

## Installation & Setup
### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/quiz-app.git
cd quiz-app
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root and add:
```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://user:password@localhost:5432/quiz_db
REDIS_URL=redis://127.0.0.1:6379/1
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Create a Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Redis (for WebSockets & Notifications)
```bash
redis-server
```

### 8. Run the Development Server
```bash
python manage.py runserver
```

---

## API Endpoints
### Authentication
- `POST /api/token/` → Get JWT token (login)
- `POST /api/token/refresh/` → Refresh JWT token

### Game Room
- `GET /api/game_room/` → List game rooms
- `POST /api/game_room/` → Create a new game room
- `GET /api/game_room/{room_code}/` → Retrieve a game room

### Players
- `POST /api/join_game/` → Join an existing game room
- `GET /api/players/` → List all players in a game

---

## WebSocket Implementation
### WebSocket URL
```
ws://127.0.0.1:8000/ws/game_lobby/{room_code}/
```

### Events
| Event | Description |
|---|---|
| `connect` | Players join the game room |
| `disconnect` | Players leave the game room |
| `send_question` | Broadcasts trivia questions |
| `submit_answer` | Player submits an answer |
| `game_over` | Ends the game and shows results |

#### Example WebSocket Message
```json
{
    "type": "send_question",
    "question": "What is the capital of France?",
    "choices": ["Paris", "London", "Berlin", "Rome"]
}
```

---

## Deployment
### Using Railway
1. Push to GitHub
2. Link GitHub repo to Railway
3. Add environment variables (`SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`)
4. Deploy & Scale!

---

## Troubleshooting
### WebSocket Not Connecting?
- Ensure Redis is running (`redis-server`)
- Check `CHANNEL_LAYERS` config in `settings.py`
- Restart Django (`python manage.py runserver`)

### Game Room Not Creating?
- Ensure user is authenticated (JWT token in `Authorization: Bearer ...` header)
- Check if the backend is correctly setting the `host`

---

## License
MIT License. See `LICENSE` file for details.

---

## Contributing
Pull requests are welcome! Open an issue for major changes.

---

## Author
[Meculos](https://github.com/Meculos)

