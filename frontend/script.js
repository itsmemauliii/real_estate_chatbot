document.addEventListener('DOMContentLoaded', () => {
    // Determine if on login/signup page or chat page based on element presence
    const loginSignupForm = document.getElementById('login-form');
    const chatBox = document.getElementById('chat-box');

    // **IMPORTANT**: If deploying, replace this with your actual deployed backend URL (e.g., Heroku, Render URL)
    // For local development, an empty string or '/' works as calls are relative to the current host.
    const API_BASE_URL = ''; // Keep empty for local development to use relative paths

    if (loginSignupForm) {
        // --- Login/Signup Logic (NO CHANGE) ---
        // ... (keep this section as it is) ...

    } else if (chatBox) {
        // --- Chatbot Logic ---
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');

        // RENAMED: from propertiesViewed to insightsExplored
        let insightsExplored = parseInt(localStorage.getItem('insightsExplored')) || 0;
        let badgesEarned = parseInt(localStorage.getItem('badgesEarned')) || 0;

        function updateGamificationUI() {
            // RENAMED: properties-viewed to insights-explored
            document.getElementById('insights-explored').textContent = insightsExplored;
            document.getElementById('badges-earned').textContent = badgesEarned;
            localStorage.setItem('insightsExplored', insightsExplored); // Updated storage key
            localStorage.setItem('badgesEarned', badgesEarned);
        }

        const appendMessage = (message, sender) => {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', `${sender}-message`);
            messageDiv.innerHTML = message;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
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
                // Adjusted conditions to trigger for relevant marketing insights
                if (data.response.includes("Commonly used marketing mediums:") ||
                    data.response.includes("Common social media platforms used:") ||
                    data.response.includes("Common digital marketing services used:") ||
                    data.response.includes("Most customer leads are generated through:") ||
                    data.response.includes("Satisfaction with lead quality:") ||
                    data.response.includes("Opinion on digital marketing cost:") ||
                    data.response.includes("For **") && data.response.includes("Marketing mediums:")) { // If project info includes marketing
                    
                    insightsExplored++; // Increment insights explored
                    if (insightsExplored > 0 && insightsExplored % 5 === 0) { // Example: earn a badge for every 5 insights explored
                        badgesEarned++;
                        appendMessage("🎉 Congratulations! You earned a 'Marketing Explorer' badge!", 'bot');
                    }
                    updateGamificationUI();
                }

            } catch (error) {
                console.error('Error sending message to chatbot:', error);
                appendMessage("Sorry, I'm having trouble connecting or processing your request. Please try again later.", 'bot');
            }
        };

        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        document.getElementById('quiz-button').addEventListener('click', () => {
            appendMessage("Welcome to the Marketing Trivia! I'll ask you some questions. For instance, 'Which digital marketing service focuses on content and SEO?'", 'bot');
            // Placeholder: Implement actual quiz logic here
        });

        updateGamificationUI(); // Initialize UI on load with stored values
    }
});
