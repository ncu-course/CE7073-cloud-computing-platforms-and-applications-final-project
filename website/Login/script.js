// Login Form Logic
document.getElementById('loginForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent form submission

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const message = document.getElementById('message');

    // Basic validation
    if (!username || !password) {
        message.textContent = 'Please fill in both fields.';
        return;
    }

    // Simulate a login process
    if (username === 'admin' && password === 'password123') {
        message.style.color = 'green';
        message.textContent = 'Login successful! Redirecting...';
        //console.log('Redirecting to ../God Bless You/index.html'); // 除錯訊息
        setTimeout(() => {
            window.location.href = '../index.html'; // Redirect to dashboard
        }, 2000);
    } else {
        message.style.color = 'red';
        message.textContent = 'Invalid username or password.';
    }
});
