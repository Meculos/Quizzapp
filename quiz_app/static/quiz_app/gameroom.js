document.addEventListener('DOMContentLoaded', () => {
    listGameRooms();

    document.getElementById('createRoom').addEventListener('click', (event) => {
        event.preventDefault()
        createGameRoom()
    })
})

async function listGameRooms() {
    const accessToken = localStorage.getItem('access_token')
    const gameRoomDiv = document.getElementById('game-room-div')

    if (!accessToken) {
        gameRoomDiv.innerHTML = `
            <div class="text-center">
                <p>
                    No user logged in. Please <a href="/quiz_app/login_page/"> Login</a>
                    or <a href="/quiz_app/register_page/"> Register</a>
                </p>
            </div>
        `;
        return;
    }

    try {
        const response = await fetch('/quiz_app/api/game_room', {
            method: 'GET',
            headers: {
                'authorization': `Bearer ${accessToken}`
            }
        })

        if (!response.ok) {
            if (response.status === 401) {
                gameRoomDiv.innerHTML = `
                    <div class="text-center">
                        <p>
                            Session Expired. Please <a href="/quiz_app/login_page/"> Login</a>
                        </p>
                    </div>
                `;
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                return;
            }
        }

        const data = await response.json()

        if (data.length === 0) {
            gameRoomDiv.innerHTML = `
                <div class="text-center">
                    <p>
                        No GameRoom created yet. <a href="#" id="createRoom" onclick="createGameRoom()">Create one now</a>
                    </p>
                </div>
            `
        } else {
            gameRoomDiv.innerHTML = data.map(room => `
                    <div class="d-flex justify-content-between align-items-center border p-2 mb-2">
                        <p class="m-0">${room.host_username}'s Game</p>
                        <a class="btn btn-outline-light" href="/quiz_app/game_room/${room.room_code}">
                            Join Game
                        </a>
                    </div>
            `).join('');
        }
    } catch(error) {
        console.log('Error retrieving gamerooms, ', error)
    }
}

async function createGameRoom() {
    const accessToken = localStorage.getItem('access_token');

    if (!accessToken) {
        alert("Please log in to create a game room.");
        return;
    }

    try {
        const response = await fetch('/quiz_app/api/game_room/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            window.location.href = `/quiz_app/game_room/${data.room_code}`;
        } else {
            const errorData = await response.json();
            alert(errorData.message || "Error creating game room.");
        }
    } catch (error) {
        console.log("Error creating game room:", error);
    }
}
