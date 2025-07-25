from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import pandas as pd
import sqlite3
import bcrypt
import os
from backend.nlp_model import predict_intent, extract_entities, get_marketing_insights # Changed import
from backend.utils import load_marketing_data # Changed import

app = Flask(__name__, template_folder='../frontend') # Point Flask to the frontend folder for templates
CORS(app) # Enable CORS for frontend interaction
# IMPORTANT: Replace with a strong, randomly generated key in production
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Load marketing data once on startup (using the new function and file)
marketing_survey_df = load_marketing_data(filepath='data/property_listings.csv.xlsx - Form responses 1.csv')

DATABASE = 'backend/users.db' # Path to your SQLite database

def init_db():
    """Initializes the SQLite database for users."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Initialize database when the app starts
with app.app_context(): # Ensure this runs within the app context
    init_db()

@app.route('/')
def home():
    """Renders the login/signup page or redirects to chat if logged in."""
    if 'username' in session:
        return redirect(url_for('chat_page'))
    return render_template('index.html') # This is your login/signup page

@app.route('/signup', methods=['POST'])
def signup():
    """Handles user registration."""
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password.decode('utf-8')))
            conn.commit()
            return jsonify({"message": "User registered successfully!"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"message": "Username already exists. Please choose a different one."}), 409
        except Exception as e:
            return jsonify({"message": f"An error occurred during signup: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login():
    """Handles user login."""
    username = request.form['username']
    password = request.form['password'].encode('utf-8')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

    if result:
        stored_password = result[0].encode('utf-8')
        if bcrypt.checkpw(password, stored_password):
            session['username'] = username
            return jsonify({"message": "Login successful!", "redirect": url_for('chat_page')}), 200
    return jsonify({"message": "Invalid username or password."}), 401

@app.route('/logout')
def logout():
    """Logs out the user."""
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/chat_page')
def chat_page():
    """Renders the chatbot interface after successful login."""
    if 'username' in session:
        return render_template('chat.html', username=session['username'])
    return redirect(url_for('home')) # Redirect to login if not authenticated

@app.route('/chat', methods=['POST'])
def chat():
    """Processes user messages and generates chatbot responses."""
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({"response": "Please enter a message."})

    intent = predict_intent(user_message)
    entities = extract_entities(user_message) # Extract entities for all intents where applicable
    response_message = ""

    if intent == "greet":
        response_message = "Hello! I'm your Real Estate Marketing Insights bot. How can I assist you with project marketing data today?"
    elif intent in ["marketing_mediums_query", "social_media_query",
                    "digital_services_query", "lead_generation_query",
                    "lead_quality_query", "cost_opinion_query", "project_info_query"]:
        response_message = get_marketing_insights(intent, entities, marketing_survey_df)
    elif intent == "thank_you":
        response_message = "You're most welcome! Is there anything else I can help you with regarding marketing insights?"
    elif intent == "goodbye":
        response_message = "Goodbye! Have a productive day with your marketing strategies. See you!"
    else:
        response_message = "I'm designed to provide insights on real estate marketing and project data. You can ask me about marketing mediums, social media platforms, lead generation, or specific projects."

    return jsonify({"response": response_message})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
