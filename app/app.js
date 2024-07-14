// Function to get JWT token from localStorage
function getJWTToken() {
    return localStorage.getItem('token');
}

// Function to get CSRF token
function getCSRFToken() {
    return document.cookie.split('; ').find(row => row.startsWith('csrf_token=')).split('=')[1];
}

let csrfToken = '';

// Function to update CSRF token
function updateCSRFToken(newToken) {
    csrfToken = newToken;
}

// Function to get current CSRF token
function getCSRFToken() {
    return csrfToken;
}

async function apiCall(url, method = 'POST', body = null) {
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': getCSRFToken()
    };

    const options = {
        method,
        headers,
        credentials: 'include', // This ensures cookies are sent with the request
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);

        // Update CSRF token from response header
        const newCSRFToken = response.headers.get('X-CSRF-TOKEN');
        if (newCSRFToken) {
            updateCSRFToken(newCSRFToken);
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.msg || 'API call failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}

// Function to handle form submissions
async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const url = form.action;
    const method = form.method.toUpperCase();

    const body = {};
    for (let [key, value] of formData.entries()) {
        body[key] = value;
    }

    try {
        const response = await apiCall(url, method, body);
        console.log('Form submitted successfully:', response);
        window.location.reload();
    } catch (error) {
        console.error('Form submission error:', error);
        alert('Form submission failed. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize CSRF token from meta tag
    const metaCSRFToken = document.querySelector('meta[name="csrf-token"]');
    if (metaCSRFToken) {
        updateCSRFToken(metaCSRFToken.getAttribute('content'));
    }

    const form = document.getElementById('budgetForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});


// Function to handle login
async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const data = await apiCall('/login', 'POST', { email, password });
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

    try {
        const userData = await apiCall(`/get_user?id=${userId}`);
        document.getElementById('userData').innerText = JSON.stringify(userData, null, 2);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to fetch user data. Please try again.');
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const url = form.action;
    const method = form.method.toUpperCase();

    const body = {};
    for (let [key, value] of formData.entries()) {
        body[key] = value;
    }

    try {
        const response = await apiCall(url, method, body);
        console.log('Form submitted successfully:', response);
        window.location.reload();
    } catch (error) {
        console.error('Form submission error:', error);
        alert('Form submission failed. Please try again.');
    }
}
