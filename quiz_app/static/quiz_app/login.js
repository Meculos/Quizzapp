document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('loginForm').addEventListener('submit', (event) => {
        event.preventDefault()
        loginUser()
    })
})

function loginUser() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const csrftoken = document.querySelector("input[name='csrfmiddlewaretoken']").value;

    fetch('/quiz_app/api/login_token/', {
        method: 'POST',
        headers: {'Content-type': 'application/json', 'X-CSRFToken': csrftoken},
        body: JSON.stringify({username: username, password: password})
    })
    .then(response => response.json())
    .then(data => {
        if (data.access && data.refresh) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')

            localStorage.setItem('access_token', data.access)
            localStorage.setItem('refresh_token', data.refresh)

            window.location.href = '/quiz_app/'
        } else {
            console.log('something went wrong')
        }
    })
    .catch(error => console.log('Error logging user in: ', error))
}