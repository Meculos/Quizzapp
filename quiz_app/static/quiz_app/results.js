document.addEventListener('DOMContentLoaded', () => {
    const score = localStorage.getItem('playerScore')
    document.getElementById('result').innerHTML = `You got ${score} questions right out of 20`

    function endGameAndRedirect(destination) {
        fetch('/quiz_app/end_game/')
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    localStorage.removeItem('playerScore');
                    localStorage.removeItem('endTime');
                    window.location.href = destination;
                }
            })
            .catch(error => console.error('Error ending game:', error));
    }
    
    document.getElementById('playAgain').addEventListener('click', () => endGameAndRedirect('/quiz_app/single_play_mode/'));
    document.getElementById('homepage').addEventListener('click', () => endGameAndRedirect('/quiz_app/'));
})