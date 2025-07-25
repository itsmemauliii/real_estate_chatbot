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
    app.run(debug=True, host='0.0.0.0', port=5000)
