document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // **IMPORTANT**: If deploying, replace this with your actual deployed backend URL (e.g., Heroku, Render URL)
    // For local development, an empty string or '/' works as calls are relative to the current host.
    const API_BASE_URL = ''; // Keep empty for local development to use relative paths

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
});
