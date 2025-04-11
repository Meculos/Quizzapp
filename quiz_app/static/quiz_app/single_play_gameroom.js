document.addEventListener('DOMContentLoaded', () => {
    let gameActive = true;

    window.addEventListener('beforeunload', function (e) {
        if (gameActive) {
            e.preventDefault();
            e.returnValue = ''; // Necessary for the dialog
        }
    });

    const timerElement = document.getElementById('timer');

    const countdownTime = 2 * 60 * 1000; // 2 minutes in milliseconds

    // Check if end time exists in localStorage
    let endTime = localStorage.getItem('endTime');

    if (!endTime) {
        endTime = new Date().getTime() + countdownTime;
        localStorage.setItem('endTime', endTime);
    } else {
        endTime = Number(endTime);
    }

    const timerInterval = setInterval(() => {
        const now = new Date().getTime();
        const distance = endTime - now;

        if (distance <= 0) {
            clearInterval(timerInterval);
            timerElement.textContent = "Time's Up";
            timerElement.style.color = 'red';
            timerElement.style.animation = 'blinker 1s linear infinite';
            alert("Time's Up");
            localStorage.removeItem('endTime'); // clear the time
            gameActive = false
            window.location.href = '/quiz_app/results/';
        } else {
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            timerElement.textContent = `Time Left: ${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

            if (distance < 30000) {
                timerElement.style.color = 'orange';
                timerElement.style.transition = 'color 0.5s ease';
            }
        }
    }, 1000);

    let score = Number(localStorage.getItem('playerScore')) || 0;
    localStorage.setItem('playerScore', score);

    // Get all question blocks
    const questions = document.querySelectorAll('.question-block');
    let currentQuestionIndex = 0;

    function showQuestion(index) {
        questions.forEach((question, i) => {
            if (i === index) {
                question.classList.add('active');
            } else {
                question.classList.remove('active');
            }
        });
    }
    showQuestion(currentQuestionIndex);    

    document.querySelectorAll('.answers').forEach(answerBlock => {
        answerBlock.addEventListener('click', (event) => {
            const answer = event.target.closest('.answer_buttons');
            if (!answer) return;

            const playerAnswer = answer.getAttribute('data-correct');

            // Disable all buttons in this block
            const allButtons = answerBlock.querySelectorAll('.answer_buttons');
            allButtons.forEach(button => {
                button.disabled = true;
            });

            // Check answer and update score
            if (playerAnswer === 'True') {
                answer.style.backgroundColor = 'green';
                score += 1;
                localStorage.setItem('playerScore', score);
            } else {
                answer.style.backgroundColor = 'red';

                // Show correct answer
                allButtons.forEach(button => {
                    if (button.getAttribute('data-correct') === 'True') {
                        button.style.backgroundColor = 'green';
                    }
                });
            }

            // Move to the next question after a short delay
            setTimeout(() => {
                currentQuestionIndex++;
                if (currentQuestionIndex < questions.length) {
                    showQuestion(currentQuestionIndex);
                } else {
                    gameActive = false
                    window.location.href = '/quiz_app/results/';
                }
            }, 1000); // 1-second delay for feedback
        });
    });


    // let score = Number(localStorage.getItem('playerScore')) || 0;
    // lStorage.setItem('playerScore', score);

    // document.querySelectorAll('.answers').forEach(answerBlock => {
    //     answerBlock.addEventListener('click', (event) => {
    //         const answer = event.target.closest('.answer_buttons');
    //         if (!answer) return; // If click was outside a button

    //         const playerAnswer = answer.getAttribute('data-correct');

    //         // Disable all buttons in this block
    //         const allButtons = answerBlock.querySelectorAll('.answer_buttons');
    //         allButtons.forEach(button => {
    //             button.disabled = true;
    //         });

    //         // Highlight clicked answer
    //         if (playerAnswer === 'True') {
    //             answer.style.backgroundColor = 'green';
    //             score += 1; // Increase score
    //             localStorage.setItem('playerScore', score); // Update localStorage
    //         } else {
    //             answer.style.backgroundColor = 'red';

    //             // Also show correct answer
    //             allButtons.forEach(button => {
    //                 if (button.getAttribute('data-correct') === 'True') {
    //                     button.style.backgroundColor = 'green';
    //                 }
    //             });
    //         }
    //     });
    // });
});

