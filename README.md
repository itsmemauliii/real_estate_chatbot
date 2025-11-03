# Real Estate Chatbot (Flask + NLP + Frontend Integration)

An intelligent real estate chatbot that helps users search, filter, and explore property listings using natural language. Built with **Flask**, **Python NLP**, and a simple **HTML/JS frontend**, this app connects user intents to real-time property recommendations.

---

## Features

* Conversational chatbot built with Flask
* NLP intent detection and entity extraction
* Property recommendations based on user input
* Data-driven backend powered by pandas
* CORS-enabled API for frontend interaction
* Smart handling of budget, location, and property type queries
* Clean structured responses with formatted prices and images

---

## Project Structure

```
real_estate_chatbot/
│
├── backend/
│   ├── app.py                 # Flask backend
│   ├── nlp_model.py           # Intent + Entity extraction logic
│   ├── utils.py               # Helper functions and data loading
│
├── frontend/
│   ├── index.html             # Chatbot UI (Flask serves this)
│   ├── static/                # CSS / JS files
│
├── data/
│   └── properties.csv         # Property dataset
│
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/real-estate-chatbot.git
cd real-estate-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # On macOS/Linux
venv\Scripts\activate         # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```
Flask
Flask-Cors
pandas
```

---

## Run the Application

```bash
cd backend
python app.py
```

* The app will start at `http://localhost:5000`
* The chatbot UI will be served from `frontend/index.html`

---

## API Endpoints

| Route   | Method | Description                                      |
| ------- | ------ | ------------------------------------------------ |
| `/`     | GET    | Serves the chatbot frontend                      |
| `/chat` | POST   | Accepts a JSON message, returns chatbot response |

### Example Request

```json
{
  "message": "Show me 2BHK apartments in Mumbai under 50 lakhs"
}
```

### Example Response

```json
{
  "response": "Here are some properties that match your criteria: ..."
}
```

---

## NLP Workflow

1. **predict_intent()** → Detects if user is greeting, searching, etc.
2. **extract_entities()** → Extracts city, budget, type, etc.
3. **get_property_recommendations()** → Matches entities to dataset.

---

## Data Format

Example `properties.csv`:

| id | type      | location | bedrooms | price   | area_sqft | description           | image_url   |
| -- | --------- | -------- | -------- | ------- | --------- | --------------------- | ----------- |
| 1  | apartment | Mumbai   | 2        | 4500000 | 900       | Near metro, furnished | https://... |

---

## Deployment

To deploy:

```bash
gunicorn app:app
```

Or use platforms like **Render**, **Railway**, or **Heroku** with a proper `Procfile`.

---

## Author

* **Mauli Patel**
* Data Science & AI Enthusiast
* [LinkedIn](https://linkedin.com/in/maulipatel)
* [maulipatel@example.com](mailto:maulipatel@example.com)

