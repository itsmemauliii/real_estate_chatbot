from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import pandas as pd
import sqlite3
import bcrypt
import os
from backend.nlp_model import predict_intent, extract_entities, get_property_recommendations
from backend.utils import load_properties_data

app = Flask(__name__, template_folder='../frontend') # Point Flask to the frontend folder for templates
CORS(app) # Enable CORS for frontend interaction
# IMPORTANT: Replace with a strong, randomly generated key in production
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Load property data once on startup
properties_df = load_properties_data(filepath='data/properties.csv')

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
    response_message = ""

    if intent == "greet":
        response_message = "Hello! How can I assist you with your real estate needs today?"
    elif intent == "property_search":
        entities = extract_entities(user_message)
        recommendations = get_property_recommendations(entities, properties_df)
        if recommendations:
            response_message = "Here are some properties that match your criteria:<br>"
            for prop in recommendations[:5]: # Limit to 5 for brevity
                price_formatted = f"₹{prop['price']:,}" # Format price with commas
                response_message += (
                    f"- **{prop['bedrooms']}BHK {prop['type'].capitalize()}** in **{prop['location'].capitalize()}** "
                    f"for **{price_formatted}** (Area: {prop['area_sqft']} sqft). "
                    f"Description: {prop['description']}. "
                )
                if 'image_url' in prop and prop['image_url']:
                    response_message += f"<a href='{prop['image_url']}' target='_blank'>View Image</a><br>"
                else:
                    response_message += "<br>"
        else:
            response_message = "Sorry, I couldn't find any properties matching your criteria. Can you try being more specific about location, type, or budget?"
    elif intent == "thank_you":
        response_message = "You're most welcome! Is there anything else I can help you with?"
    elif intent == "goodbye":
        response_message = "Goodbye! Hope you find your dream property soon. See you!"
    elif intent == "budget_query":
        response_message = "What's your preferred budget or price range for the property?"
    elif intent == "location_query":
        response_message = "Which location or city are you interested in?"
    elif intent == "contact":
        response_message = "Sure, I can connect you with an agent. Please provide your contact number or email, and they'll get in touch shortly."
    elif intent == "more_details":
         # This intent would typically require a property ID or some context from previous turns
        response_message = "Which property would you like more details about? Please provide a property ID or describe it."
    else:
        response_message = "I'm still learning and might not understand that. Can you please ask about properties, locations, or your budget?"

    return jsonify({"response": response_message})

if __name__ == '__main__':
    # Use 0.0.0.0 for deployment to make it accessible externally (e.g., in a Docker container or server)
    # For local development, debug=True is fine.
    app.run(debug=True, host='0.0.0.0', port=5000)
