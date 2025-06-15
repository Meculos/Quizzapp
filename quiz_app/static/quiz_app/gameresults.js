document.addEventListener('DOMContentLoaded', () => {
    const roomCode = document.getElementById('roomcode').getAttribute('data-room-code')

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws/game_lobby/${roomCode}/`);


    socket.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === 'display_results') {
            displayResults(data.results)
        } else if (data.type === 'finish_game') {
             window.location.href = '/quiz_app/'
        }
    }

    function displayResults(results) {
        const resultsContainer = document.querySelector(".result-container");
        resultsContainer.innerHTML = "";

        results.forEach(result => {
            let resultElement = document.createElement("div");
            resultElement.classList.add("d-flex", "justify-content-between", "align-items-center", "border", "p-2", "mb-2");

            let username = document.createElement("p");
            username.classList.add("m-0");
            username.textContent = result.username;

            let score = document.createElement("p");
            score.classList.add("m-0");
            score.textContent = result.score;

            resultElement.appendChild(username);
            resultElement.appendChild(score);
            resultsContainer.appendChild(resultElement);
        });

        // Add the "To Homepage" button
        const buttonContainer = document.createElement("div");
        buttonContainer.classList.add("d-flex", "justify-content-center");

        const button = document.createElement("button");
        button.classList.add("btn", "btn-outline-info");
        button.textContent = "To Homepage";
        button.onclick = finishGame;

        buttonContainer.appendChild(button);
        resultsContainer.appendChild(buttonContainer);
    }

    function finishGame() {
        socket.send(JSON.stringify({
            type: 'finish_game'
        }))
    }
})