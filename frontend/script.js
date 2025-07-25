document.addEventListener('DOMContentLoaded', () => {
    // Determine if on login/signup page or chat page based on element presence
    const loginSignupForm = document.getElementById('login-form');
    const chatBox = document.getElementById('chat-box');

    // **IMPORTANT**: If deploying, replace this with your actual deployed backend URL (e.g., Heroku, Render URL)
    // For local development, an empty string or '/' works as calls are relative to the current host.
    const API_BASE_URL = ''; // Keep empty for local development to use relative paths

    if (loginSignupForm) {
        // --- Login/Signup Logic ---
        const signupForm = document.getElementById('signup-form');
        const loginForm = document.getElementById('login-form');
        const signupMessage = document.getElementById('signup-message');
        const loginMessage = document.getElementById('login-message');
        const formTitle = document.getElementById('form-title');

        // Initially show login form
        signupForm.style.display = 'none';
        loginForm.style.display = 'block';

        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('signup-username').value;
            const password = document.getElementById('signup-password').value;

            // Simple validation
            if (username.length < 3) {
                signupMessage.textContent = 'Username must be at least 3 characters.';
                signupMessage.style.color = 'red';
                return;
            }
            if (password.length < 6) {
                signupMessage.textContent = 'Password must be at least 6 characters.';
                signupMessage.style.color = 'red';
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/signup`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
                });
                const data = await response.json();
                signupMessage.textContent = data.message;
                signupMessage.style.color = response.ok ? 'green' : 'red';
                if (response.ok) {
                    signupForm.reset(); // Clear form on success
                    // Automatically switch to login form after successful signup
                    formTitle.textContent = 'Login';
                    loginForm.style.display = 'block';
                    signupForm.style.display = 'none';
                    loginMessage.textContent = 'Account created! Please log in.';
                    loginMessage.style.color = 'green';
                }
            } catch (error) {
                signupMessage.textContent = 'An error occurred. Please try again.';
                signupMessage.style.color = 'red';
                console.error('Signup error:', error);
            }
        });

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            try {
                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
                });
                const data = await response.json();
                loginMessage.textContent = data.message;
                loginMessage.style.color = response.ok ? 'green' : 'red';

                if (response.ok && data.redirect) {
                    window.location.href = data.redirect; // Redirect to chat page
                }
            } catch (error) {
                loginMessage.textContent = 'An error occurred during login. Please try again.';
                loginMessage.style.color = 'red';
                console.error('Login error:', error);
            }
        });

        // Toggle between login and signup forms
        const toggleSignup = document.getElementById('toggle-signup');
        const toggleLogin = document.getElementById('toggle-login');

        if (toggleSignup) {
            toggleSignup.addEventListener('click', (e) => {
                e.preventDefault();
                formTitle.textContent = 'Sign Up';
                loginForm.style.display = 'none';
                signupForm.style.display = 'block';
                signupMessage.textContent = ''; // Clear messages
                loginMessage.textContent = '';
            });
        }

        if (toggleLogin) {
            toggleLogin.addEventListener('click', (e) => {
                e.preventDefault();
                formTitle.textContent = 'Login';
                signupForm.style.display = 'none';
                loginForm.style.display = 'block';
                signupMessage.textContent = ''; // Clear messages
                loginMessage.textContent = '';
            });
        }


    } else if (chatBox) {
        // --- Chatbot Logic ---
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');

        // Gamification variables
        let propertiesViewed = parseInt(localStorage.getItem('propertiesViewed')) || 0;
        let badgesEarned = parseInt(localStorage.getItem('badgesEarned')) || 0;

        function updateGamificationUI() {
            document.getElementById('properties-viewed').textContent = propertiesViewed;
            document.getElementById('badges-earned').textContent = badgesEarned;
            localStorage.setItem('propertiesViewed', propertiesViewed);
            localStorage.setItem('badgesEarned', badgesEarned);
        }

        const appendMessage = (message, sender) => {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', `${sender}-message`);
            messageDiv.innerHTML = message; // Use innerHTML to allow for HTML tags in bot response
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
        };

        const sendMessage = async () => {
            const message = userInput.value.trim();
            if (message === '') return;

            appendMessage(message, 'user');
            userInput.value = '';

            try {
                const response = await fetch(`${API_BASE_URL}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                });
                const data = await response.json();
                appendMessage(data.response, 'bot');

                // Gamification update based on bot's response
                if (data.response.includes("Here are some properties")) {
                    propertiesViewed++;
                    if (propertiesViewed > 0 && propertiesViewed % 5 === 0) { // Example: earn a badge for every 5 properties viewed
                        badgesEarned++;
                        appendMessage("🎉 Congratulations! You earned a 'Property Explorer' badge!", 'bot');
                    }
                    updateGamificationUI();
                }

            } catch (error) {
                console.error('Error sending message:', error);
                appendMessage("Sorry, I'm having trouble connecting. Please try again later.", 'bot');
            }
        };

        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        document.getElementById('quiz-button').addEventListener('click', () => {
            appendMessage("Welcome to the Property Quiz! I'll ask you some questions about real estate. Answer correctly to earn bonus points!", 'bot');
            // Implement quiz logic here (e.g., send a specific intent to backend to start quiz)
            // For now, this is just a placeholder.
        });

        updateGamificationUI(); // Initialize UI on load
    }
});
