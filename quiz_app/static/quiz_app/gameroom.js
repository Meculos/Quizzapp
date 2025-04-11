document.addEventListener('DOMContentLoaded', () => {
    listGameRooms();

    document.getElementById('createRoom').addEventListener('click', (event) => {
        event.preventDefault()
        createGameRoom()
    })
})

async function listGameRooms() {
    const gameRoomDiv = document.getElementById('game-room-div');

    try {
        const data = await fetchWithToken('/quiz_app/api/game_room', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!data) return;  // If user is logged out, stop execution

        if (data.length === 0) {
            gameRoomDiv.innerHTML = `
                <div class="text-center">
                    <p>
                        No GameRoom created yet. <a href="#" id="createRoom" onclick="createGameRoom()">Create one now</a>
                    </p>
                </div>
            `;
        } else {
            document.getElementById('createGameButton').innerHTML = `
                    <div class="d-flex justify-content-center">
                        <button id="creategame" onclick="createGameRoom()">
                            Create a new gameroom
                        </button>
                    </div>
            `
            gameRoomDiv.innerHTML = data.map(room => `
                    <div class="d-flex justify-content-center">
                        <p class="mb-4" onclick="createGameRoom()" style=color: blue;>
                            Create a new gameroom
                        </p>
                    </div>

                    <div class="d-flex justify-content-between align-items-center border p-2 mb-2">
                        <p class="m-0">${room.host_username}'s Game</p>
                        <a class="btn btn-outline-light" href="/quiz_app/game_room/${room.room_code}">
                            Join Game
                        </a>
                    </div>
            `).join('');
        }
    } catch (error) {
        console.log('Error retrieving gamerooms:', error);
    }
}

async function createGameRoom() {
    try {
        const data = await fetchWithToken('/quiz_app/api/game_room/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (data?.room_code) {
            window.location.href = `/quiz_app/game_room/${data.room_code}`;
        } else {
            alert(data?.message || "Error creating game room.");
        }
    } catch (error) {
        console.log("Error creating game room:", error);
    }
}

async function fetchWithToken(url, options = {}) {
    const csrfToken = getCSRFToken();

    // Ensure headers exist
    options.headers = options.headers || {};

    // Add CSRF token for unsafe requests
    if (["POST", "PUT", "DELETE"].includes(options.method?.toUpperCase())) {
        options.headers["X-CSRFToken"] = csrfToken;
    }

    // Always include credentials (cookies)
    options.credentials = "include";

    let response = await fetch(url, options);

    if (response.status === 403) {
        console.log("403 Forbidden - Possible CSRF issue or permission error");
    }

    if (response.status === 401) {
        console.log("Access token expired, attempting refresh...");

        const refreshResponse = await fetch("/quiz_app/refresh_token/", {
            method: "POST",
            credentials: "include"
        });

        if (refreshResponse.ok) {
            console.log("Token refreshed, retrying request...");
            response = await fetch(url, options);
        } else {
            console.log("Refresh token expired, forcing logout...");
            window.location.href = "/quiz_app/login_page/";
            return;
        }
    }

    return response.json();
}

function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}
