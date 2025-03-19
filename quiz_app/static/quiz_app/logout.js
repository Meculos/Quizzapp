document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('logoutBtn').addEventListener('click', (event) => {
        event.preventDefault()
        logoutUser()
    })
})

function logoutUser() {
    fetch('/quiz_app/logout/', {
        method: 'POST',
        headers: {'X-CSRFToken': getCSRFToken()}
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            window.location.href = '/quiz_app/'
        }
    })
    .catch(error => console.log('Error logging user out: ', error))
}

function getCSRFToken() {
    let cookieValue = null;
    const cookies = document.cookie.split(';');

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith('csrftoken=')) {
            cookieValue = cookie.substring('csrftoken='.length);
            break;
        }
    }

    return cookieValue;
}
