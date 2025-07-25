from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import os
from backend.nlp_model import predict_intent, extract_entities, get_property_recommendations
from backend.utils import load_properties_data

# Initialize Flask app
# Point Flask to the frontend folder for templates
app = Flask(__name__, template_folder='../frontend')
CORS(app) # Enable CORS for frontend interaction

# Load property data once on startup
# Ensure this path is correct relative to where app.py is run from (usually the project root)
properties_df = load_properties_data(filepath='data/properties.csv')

@app.route('/')
def home():
    """Renders the main chatbot interface."""
    return render_template('index.html') # This is now your single chatbot page

@app.route('/chat', methods=['POST'])
def chat():
    """Processes user messages and generates chatbot responses."""
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({"response": "Please enter a message."})

    intent = predict_intent(user_message)
    response_message = ""

    if intent == "greet":
        response_message = "Hello! I'm your Real Estate Chatbot. How can I help you find your dream property today?"
    elif intent == "property_search":
        entities = extract_entities(user_message)
        recommendations = get_property_recommendations(entities, properties_df)
        if recommendations:
            response_message = "Here are some properties that match your criteria:<br>"
            for prop in recommendations[:5]: # Limit to 5 for brevity
                # Safely get values, converting to string and capitalizing if needed
                # Use .get() with a default value like 'N/A' or an empty string to avoid KeyError if a column is truly missing,
                # and str() to ensure it's a string before calling .capitalize()
                bedrooms = prop.get('bedrooms', 'N/A')
                prop_type = str(prop.get('type', 'N/A')).capitalize()
                location = str(prop.get('location', 'N/A')).capitalize()
                area_sqft = prop.get('area_sqft', 'N/A')
                price = prop.get('price', 0) # Default to 0 if price is missing
                description = str(prop.get('description', 'No description provided.')).strip() # Default and strip whitespace

                price_formatted = f"₹{price:,}" # Format price with commas

                response_message += (
                    f"- **{bedrooms}BHK {prop_type}** in **{location}** "
                    f"for **{price_formatted}** (Area: {area_sqft} sqft). "
                    f"Description: {description}. "
                )
                # Check for image_url existence and validity
                image_url = prop.get('image_url')
                if image_url and isinstance(image_url, str) and image_url.strip(): # Ensure it's a non-empty string
                    response_message += f"<a href='{image_url}' target='_blank'>View Image</a><br>"
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
    app.run(debug=True, host='0.0.0.0', port=5000)
