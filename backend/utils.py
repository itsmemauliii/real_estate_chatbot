import pandas as pd
import spacy

# Load a pre-trained spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy 'en_core_web_sm' model not found. Downloading...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def load_properties_data(filepath='data/properties.csv'):
    """Loads and preprocesses property data."""
    df = pd.read_csv(filepath)
    # Ensure 'type' and 'location' columns are treated as strings and lowercased for consistent matching
    df['type'] = df['type'].astype(str).str.lower()
    df['location'] = df['location'].astype(str).str.lower()
    return df

def preprocess_text(text):
    """Basic text preprocessing using spaCy."""
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)
