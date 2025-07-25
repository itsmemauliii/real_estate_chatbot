import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from backend.utils import preprocess_text, load_marketing_data
import re

# Load data at the module level
marketing_data_df = load_marketing_data(filepath='data/property_listings.csv.xlsx - Form responses 1.csv')

# Updated intents for marketing survey data
intents_data = {
    "greet": ["hi", "hello", "hey", "how are you", "good morning", "good evening"],
    "marketing_mediums_query": [
        "what marketing mediums are used", "how do you advertise",
        "what advertising methods do you use", "marketing channels",
        "how projects are marketed"
    ],
    "social_media_query": [
        "which social media platforms", "social media presence",
        "what social media do you use", "instagram", "facebook", "youtube"
    ],
    "digital_services_query": [
        "what digital marketing services", "digital services",
        "what services are used for digital marketing"
    ],
    "lead_generation_query": [
        "how leads are generated", "lead sources", "customer leads",
        "where do customers come from"
    ],
    "lead_quality_query": [
        "quality of leads", "lead satisfaction", "are leads good"
    ],
    "cost_opinion_query": [
        "is digital marketing costly", "cost of digital marketing",
        "is it expensive"
    ],
    "project_info_query": [
        "tell me about project", "what is project", "project details",
        "info about project", "project name"
    ],
    "thank_you": ["thanks", "thank you", "appreciate it", "cheers"],
    "goodbye": ["bye", "goodbye", "see you", "farewell"],
    "unknown": []
}

# Training intent classifier
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
    if intent_model.predict_proba([processed_text]).max() < 0.4: # Adjustable threshold
        return "unknown"
    return prediction

def extract_entities(text):
    """
    Extracts entities relevant to the marketing survey data.
    E.g., project names, marketing mediums.
    """
    entities = {}
    text_lower = text.lower()

    # Project Name extraction (very basic, consider a predefined list or more advanced NER)
    # Example: "Tell me about The Creston"
    project_names_in_data = marketing_data_df['project_name'].unique()
    for name in project_names_in_data:
        if name.lower() in text_lower:
            entities['project_name'] = name
            break

    # Marketing medium extraction (basic keyword matching)
    marketing_keywords = ['social media', 'online portals', 'newspaper', 'bill boards',
                          'digital media', 'email marketing', 'whatsapp marketing',
                          'influencer marketing', 'radio']
    for keyword in marketing_keywords:
        if keyword in text_lower:
            entities['marketing_medium'] = keyword
            break

    return entities

def get_marketing_insights(intent, entities, df):
    """
    Provides insights or information based on the intent and extracted entities
    from the marketing survey data.
    """
    response_parts = []
    filtered_df = df.copy()

    if 'project_name' in entities:
        filtered_df = filtered_df[filtered_df['project_name'] == entities['project_name']]
        if filtered_df.empty:
            return f"I couldn't find details for a project named '{entities['project_name'].title()}'."
        response_parts.append(f"For **{entities['project_name'].title()}**:")

    if intent == "marketing_mediums_query":
        if not filtered_df.empty:
            mediums = filtered_df['marketing_mediums'].explode().unique()
            if len(mediums) > 0:
                response_parts.append(f"Commonly used marketing mediums: {', '.join([m.title() for m in mediums if m and m != 'nan'])}.")
            else:
                response_parts.append("Marketing mediums data not available for this query.")
        else:
            response_parts.append("What project or type of marketing are you interested in?")

    elif intent == "social_media_query":
        if not filtered_df.empty:
            platforms = filtered_df['social_media_platforms'].explode().unique()
            if len(platforms) > 0:
                response_parts.append(f"Common social media platforms used: {', '.join([p.title() for p in platforms if p and p != 'nan'])}.")
            else:
                response_parts.append("Social media platforms data not available for this query.")
        else:
            response_parts.append("Please specify a project or a general query about social media.")

    elif intent == "digital_services_query":
        if not filtered_df.empty:
            services = filtered_df['digital_marketing_services'].explode().unique()
            if len(services) > 0:
                response_parts.append(f"Common digital marketing services used: {', '.join([s.title() for s in services if s and s != 'nan'])}.")
            else:
                response_parts.append("Digital marketing services data not available for this query.")
        else:
            response_parts.append("What digital marketing services are you curious about?")

    elif intent == "lead_generation_query":
        if not filtered_df.empty:
            sources = filtered_df['lead_generation_sources'].explode().unique()
            if len(sources) > 0:
                response_parts.append(f"Most customer leads are generated through: {', '.join([s.title() for s in sources if s and s != 'nan'])}.")
            else:
                response_parts.append("Lead generation sources data not available for this query.")
        else:
            response_parts.append("What project or lead generation topic are you interested in?")

    elif intent == "lead_quality_query":
        if not filtered_df.empty:
            qualities = filtered_df['lead_quality_satisfaction'].unique()
            opinions = filtered_df['digital_lead_quality_opinion'].unique()
            response_parts.append(f"Satisfaction with lead quality: {', '.join([q.title() for q in qualities if q and q != 'nan'])}. Opinion on digital lead quality: {', '.join([o.title() for o in opinions if o and o != 'nan'])}.")
        else:
            response_parts.append("Please specify a project or a general query about lead quality.")

    elif intent == "cost_opinion_query":
        if not filtered_df.empty:
            cost_opinions = filtered_df['cost_opinion_digital_marketing'].unique()
            if len(cost_opinions) > 0:
                response_parts.append(f"Opinion on digital marketing cost: {', '.join([o.title() for o in cost_opinions if o and o != 'nan'])}.")
            else:
                response_parts.append("Cost opinion data not available for this query.")
        else:
            response_parts.append("What specific cost are you inquiring about?")

    elif intent == "project_info_query":
        if not filtered_df.empty:
            if 'project_name' not in entities: # If no specific project was mentioned, list some
                response_parts.append(f"I have information on projects like: {', '.join(df['project_name'].unique()[:3].tolist())}. Which project are you interested in?")
            else:
                project_row = filtered_df.iloc[0] # Take the first matching project
                response_parts.append(f"**{project_row['project_name'].title()}** at {project_row['address'].title()} has mobile number {project_row['mobile_number']}.")
                response_parts.append(f"Marketing mediums: {project_row['marketing_mediums'].title()}. Social Media: {project_row['social_media_platforms'].title()}.")
                response_parts.append(f"Digital Services: {project_row['digital_marketing_services'].title()}.")
                response_parts.append(f"Lead sources: {project_row['lead_generation_sources'].title()}.")
        else:
            response_parts.append("I can tell you about specific projects if you provide the name.")

    # Default fallback if no specific intent handled
    if not response_parts:
        response_parts.append("I can provide insights on marketing mediums, social media, digital services, lead generation, or project details from the survey data.")

    return " ".join(response_parts)
