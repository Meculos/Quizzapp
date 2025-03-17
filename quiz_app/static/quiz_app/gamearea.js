document.addEventListener('DOMContentLoaded', () => {
    const roomCode = document.getElementById('roomcode').getAttribute('data-room-code')

    const socket = new WebSocket(`ws://${window.location.host}/ws/game_area/${roomCode}/`)

    let timerInterval;

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.type === "game_start") {
            displayQuestions(data.game_data);
            const endTime = new Date(data.game_data.end_time).getTime();  // Use server-provided end time
            startTimer(endTime);
        } 
        else if (data.type === "game_end") {
            alert("Time's up! Redirecting to results page...");
            window.location.href = `/quiz_app/game_results/${roomCode}/`;
        } else if (data.type === "update_scores") {
            updateScoreboard(data.scores);
        }
    }

    function displayQuestions(gameData) {
        const questionsContainer = document.querySelector(".question-container");
        questionsContainer.innerHTML = "";  // Clear previous content
        questionsContainer.style.display = "flex";
        questionsContainer.style.flexDirection = "column";
        questionsContainer.style.alignItems = "center";
        questionsContainer.style.gap = "20px"; // Space between questions
    
        const categoryDiv = document.getElementById('category');
        categoryDiv.innerHTML = `
            <h2 style="text-align: center; color: white;">Category: <strong>${gameData.category}</strong></h2>
        `;
    
        gameData.questions.forEach((question, index) => {
            let questionElement = document.createElement("div");
            questionElement.classList.add("question-card");
    
            let questionText = document.createElement("p");
            questionText.textContent = `${index + 1}. ${question.question_text}`;
            questionElement.appendChild(questionText);
    
            let shuffledAnswers = question.answers;
            let answersContainer = document.createElement("div");
            answersContainer.style.display = "flex";
            answersContainer.style.flexDirection = "column";
            answersContainer.style.gap = "8px"; // Space between answers
    
            shuffledAnswers.forEach(answer => {
                let answerDiv = document.createElement("div");
                answerDiv.classList.add("answer-option");
    
                let input = document.createElement("input");
                input.type = "radio";
                input.name = `question-${index}`;
                input.classList.add("answer-input");
                input.setAttribute("data-correct", answer === question.correct_answer);
                input.onclick = () => submitAnswer(question.id, answer);
    
                let label = document.createElement("label");
                label.textContent = answer;
    
                answerDiv.appendChild(input);
                answerDiv.appendChild(label);
                answersContainer.appendChild(answerDiv);
            });
    
            questionElement.appendChild(answersContainer);
            questionsContainer.appendChild(questionElement);
        });
    }    

    let timerStarted = false;  // Prevent multiple timers

    function startTimer(endTime) {
        if (timerStarted) return;  // Prevent multiple timers
        timerStarted = true;
    
        const timerElement = document.getElementById("timer");
        if (!timerElement) {
            console.error("Timer element not found!");
            return;
        }
    
        timerInterval = setInterval(() => {
            let now = new Date().getTime();
            let distance = endTime - now;
    
            if (distance <= 0) {
                console.log("Timer reached zero, clearing interval...");
                clearInterval(timerInterval);
                timerElement.textContent = "Time's Up!"; // Change text
                socket.send(JSON.stringify({ type: "end_game" }));  // Notify server
            } else {
                let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                let seconds = Math.floor((distance % (1000 * 60)) / 1000);
                timerElement.textContent = `Time Left: ${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
            }
        }, 1000);
    }    

    function submitAnswer(questionId, answer) {
        socket.send(JSON.stringify({
            type: "submit_answer",
            question_id: questionId,
            answer: answer
        }));
    }

    function updateScoreboard(scores) {
        const scoreboard = document.getElementById("scoreboard");
        scoreboard.innerHTML = "";
    
        scores.forEach(player => {
            let playerElement = document.createElement("p");
            playerElement.textContent = `${player.username}: ${player.score}`;
            scoreboard.appendChild(playerElement);
        });
    }
})