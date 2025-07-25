import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from backend.utils import preprocess_text, load_properties_data
import re

# For a simple intent classification example
intents_data = {
    "greet": ["hi", "hello", "hey", "how are you", "good morning", "good evening"],
    "property_search": [
        "find property", "look for apartment", "search for house", "show me properties",
        "I want to buy a flat", "looking for a villa", "find me a home", "properties in",
        "apartment with", "house with", "flat in", "looking to rent", "looking to buy"
    ],
    "thank_you": ["thanks", "thank you", "appreciate it", "cheers"],
    "goodbye": ["bye", "goodbye", "see you", "farewell"],
    "more_details": ["tell me more", "details", "info", "what about this"],
    "budget_query": ["what's the price", "how much does it cost", "budget", "price range"],
    "location_query": ["where is it located", "location", "area"],
    "contact": ["contact agent", "talk to someone", "need help", "can I speak to someone"]
}

# Training a simple intent classifier
def train_intent_model(intents_dict):
    X = []
    y = []
    for intent, phrases in intents_dict.items():
        for phrase in phrases:
            X.append(preprocess_text(phrase))
            y.append(intent)

    model = make_pipeline(TfidfVectorizer(), SVC(kernel='linear', probability=True))
    model.fit(X, y)
    return model

intent_model = train_intent_model(intents_data)

def predict_intent(text):
    processed_text = preprocess_text(text)
    prediction = intent_model.predict([processed_text])[0]
    # Use confidence to determine if it's an "unknown" intent
    if intent_model.predict_proba([processed_text]).max() < 0.4: # Adjustable threshold
        return "unknown"
    return prediction

def extract_entities(text):
    """
    Extracts entities like property type, location, bedrooms, price range.
    This uses a rule-based approach for simplicity.
    """
    entities = {}
    text_lower = text.lower()

    # Property type
    if re.search(r'\b(apartment|flat|house|villa)\b', text_lower):
        if 'apartment' in text_lower or 'flat' in text_lower:
            entities['type'] = 'apartment'
        elif 'house' in text_lower:
            entities['type'] = 'house'
        elif 'villa' in text_lower:
            entities['type'] = 'villa'

    # Bedrooms
    bedroom_match = re.search(r'(\d+)\s*(bhk|bedroom|bed)', text_lower)
    if bedroom_match:
        entities['bedrooms'] = int(bedroom_match.group(1))

    # Location (simplified, needs a comprehensive list of known locations)
    # For a real project, consider using a named entity recognition (NER) model
    # or a more extensive gazetteer for locations.
    known_locations = ['mumbai', 'delhi', 'bangalore', 'pune', 'chennai', 'hyderabad', 'kolkata', 'ahmedabad']
    for loc in known_locations:
        if loc in text_lower:
            entities['location'] = loc
            break

    # Price range (using regex for flexibility)
    # Examples: "under 50 lakhs", "50 lakhs", "1 crore", "between 30 and 40 lakhs"
    price_match_under = re.search(r'under\s*(\d+)\s*(lakh|lakhs|million|crore|crores)', text_lower)
    if price_match_under:
        price_val = int(price_match_under.group(1))
        unit = price_match_under.group(2)
        if 'lakh' in unit:
            entities['max_price'] = price_val * 100000
        elif 'million' in unit:
            entities['max_price'] = price_val * 1000000
        elif 'crore' in unit:
            entities['max_price'] = price_val * 10000000
    else: # Try to catch exact price mentioned without "under"
        price_match_exact = re.search(r'(\d+)\s*(lakh|lakhs|million|crore|crores)', text_lower)
        if price_match_exact:
            price_val = int(price_match_exact.group(1))
            unit = price_match_exact.group(2)
            if 'lakh' in unit:
                entities['price'] = price_val * 100000
            elif 'million' in unit:
                entities['price'] = price_val * 1000000
            elif 'crore' in unit:
                entities['price'] = price_val * 10000000

    return entities

def get_property_recommendations(entities, properties_df):
    """Filters properties based on extracted entities."""
    filtered_df = properties_df.copy()

    if 'type' in entities:
        filtered_df = filtered_df[filtered_df['type'].str.lower() == entities['type'].lower()]
    if 'bedrooms' in entities:
        filtered_df = filtered_df[filtered_df['bedrooms'] == entities['bedrooms']]
    if 'location' in entities:
        filtered_df = filtered_df[filtered_df['location'].str.lower() == entities['location'].lower()]
    if 'max_price' in entities:
        filtered_df = filtered_df[filtered_df['price'] <= entities['max_price']]
    elif 'price' in entities: # For exact price match, consider a range around it
        filtered_df = filtered_df[
            (filtered_df['price'] >= entities['price'] * 0.9) &
            (filtered_df['price'] <= entities['price'] * 1.1)
        ]

    return filtered_df.to_dict(orient='records')
