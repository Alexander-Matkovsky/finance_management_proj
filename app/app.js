// Function to handle login
async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            throw new Error('Login failed');
        }

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        
        // Hide login form and show user data section
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('userDataSection').style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        alert('Login failed. Please try again.');
    }
}

// Function to get user data
async function getUserData() {
    const userId = document.getElementById('userId').value;
    const token = localStorage.getItem('token');

    if (!token) {
        alert('Please login first');
        return;
    }

    try {
        const response = await fetch(`/get_user?id=${userId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }

        const userData = await response.json();
        document.getElementById('userData').innerText = JSON.stringify(userData, null, 2);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to fetch user data. Please try again.');
    }
}

// Check if token exists on page load
window.onload = function() {
    if (localStorage.getItem('token')) {
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('userDataSection').style.display = 'block';
    }
};

// Function to get CSRF token from the page
function getCSRFToken() {
    return document.querySelector('input[name="csrf_token"]').value;
}

// Updated apiCall function
async function apiCall(url, method = 'GET', body = null) {
    const token = localStorage.getItem('token');
    const csrfToken = getCSRFToken();
    
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    console.log("Making API call with CSRF token:", csrfToken);

    try {
        const response = await fetch(url, {
            method,
            headers,
            body: body ? JSON.stringify(body) : null,
            credentials: 'same-origin', // This is important for including cookies
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = '/login';
                return;
            }
            throw new Error('API call failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}

// We'll remove the form submission handler to allow normal form submissions
// If you want to handle form submissions via AJAX in the future, you can add it back

document.addEventListener('DOMContentLoaded', function() {
    console.log("JavaScript loaded. CSRF token:", getCSRFToken());
});