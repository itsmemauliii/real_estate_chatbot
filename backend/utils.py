import pandas as pd
import spacy

# Load a pre-trained spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy 'en_core_web_sm' model not found. Downloading...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def load_marketing_data(filepath='data/property_listings.csv.xlsx - Form responses 1.csv'):
    """Loads and preprocesses marketing survey data."""
    df = pd.read_csv(filepath)

    # Rename columns for easier access (optional, but good practice)
    # Adjust these based on the exact column names in your CSV if they differ
    df.rename(columns={
        'Timestamp': 'timestamp',
        'Project Name': 'project_name',
        'Address': 'address',
        'Mobile Number': 'mobile_number',
        'What types of mediums are used to advertise or market the project? (you can select multiple options)   ': 'marketing_mediums',
        'On which Social Media platforms, project presence is there? (you can select multiple options)   ': 'social_media_platforms',
        'Which Digital Marketing Services / Social Media Marketing Services are you using currently? (you can select multiple options)   ': 'digital_marketing_services',
        'How do most of your customers leads are generated? (you can select multiple options)   ': 'lead_generation_sources',
        'How satisfied are you with the quality of leads of prospect customers you received from Online websites or Digital Marketing Services?   ': 'lead_quality_satisfaction',
        'As per your opinion, what is the quality of leads if they are generated through digital marketing?   ': 'digital_lead_quality_opinion',
        'In your View, Digital Marketing Services are costly in compare to other traditional marketing?   ': 'cost_opinion_digital_marketing',
        # Add other columns if you plan to use them
    }, inplace=True)

    # Convert relevant columns to lowercase for easier searching
    for col in ['project_name', 'address', 'marketing_mediums',
                'social_media_platforms', 'digital_marketing_services',
                'lead_generation_sources', 'lead_quality_satisfaction',
                'digital_lead_quality_opinion', 'cost_opinion_digital_marketing']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower()
            # Clean up extra spaces/quotes that might come from CSV export
            df[col] = df[col].apply(lambda x: ', '.join([item.strip().replace('"', '') for item in x.split(',')]) if isinstance(x, str) else x)

    return df

def preprocess_text(text):
    """Basic text preprocessing using spaCy."""
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)
