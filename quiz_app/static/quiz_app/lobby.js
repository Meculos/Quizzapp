document.addEventListener('DOMContentLoaded', () => {
    const roomCode = document.getElementById('roomcodediv').getAttribute('data-room-code')
    const getHost = document.getElementById('ishost').getAttribute('data-is-host')
    const isHost = getHost === 'True'

    const startGameBtn = document.getElementById("start-game-btn");

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws/game_lobby/${roomId}/`);


    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === "start_game") {
            window.location.href = `/quiz_app/game_room/${roomCode}/game_area/`;  // Redirect all players
        }
        
        const playerListDiv = document.getElementById("player-list");

        playerListDiv.innerHTML = "";  // Clear existing list

        data.players.forEach(player => {
            const readyClass = player.is_ready ? "list-group-item-success" : "";
            playerListDiv.innerHTML += `
                <div class="list-group-item d-flex mb-3 justify-content-between ${readyClass}">
                    <span>${player.username}</span>
                    ${player.is_ready ? "<span>✅ Ready</span>" : "<button class='btn btn-primary ready-btn' data-id='" + player.id + "'>Ready</button>"}
                </div>
            `;
        });

        // Enable start button if all players are ready
        if (isHost && data.all_ready) {
            startGameBtn.removeAttribute("disabled");
        }
    };

    // Handle ready button clicks
    document.addEventListener("click", function(event) {
        if (event.target.classList.contains("ready-btn")) {
            const playerId = event.target.dataset.id;
            socket.send(JSON.stringify({ action: "ready_up", player_id: playerId }));
        }
    });

    // Handle start game button
    if (isHost) {
        startGameBtn.addEventListener("click", function() {
            socket.send(JSON.stringify({ action: "start_game" }));
        });
    }
})