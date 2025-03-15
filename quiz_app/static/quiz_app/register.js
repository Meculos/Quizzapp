document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('registerForm').addEventListener('submit', (event) => {
        event.preventDefault()
        registerUser()
    })
})

function registerUser() {
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password1 = document.getElementById('password1').value;
    const password2 = document.getElementById('password2').value;
    const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;

    fetch('/quiz_app/register/', {
        method: 'POST',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            username: username,
            email: email,
            password1: password1,
            password2: password2
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message)
            window.location.href = '/quiz_app/login_page/'
        } else {
            alert(data.error)
        }
    })
    .catch(error => console.log("Error registering user; ", error))
}