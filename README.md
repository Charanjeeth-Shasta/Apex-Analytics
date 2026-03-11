# Apex Analytics

**Conversational AI for Instant Business Intelligence Dashboards**

Turn any CSV into interactive charts using plain English — powered by Google Gemini, Flask, and Streamlit.

---

## Setup

### 1. Install requirements
```bash
pip install -r requirements.txt
```

### 2. Add your Gemini API key
Edit `.env`:
```
GEMINI_API_KEY="your_key_here"
```

### 3. Start the Flask backend *(Terminal 1)*
```bash
python server.py
```

### 4. Start Streamlit *(Terminal 2)*
```bash
python run_app.py
```

---

## App Flow

```
Landing Page  →  Sign Up / Log In  →  Dashboard (ChatGPT-style)
```

- **Landing page** — Product overview and features
- **Auth page** — Create account or log in (username 5-20 chars, strong password required)
- **Dashboard** — Upload a CSV, ask questions, get instant charts. Follow up to alter charts.

---

## Project Structure

```
Apex-Analytics/
├── app.py                  # Landing page
├── server.py               # Flask backend (auth + chat)
├── run_app.py              # Streamlit launcher (Python 3.14 patch)
├── requirements.txt
├── .env                    # API keys (never commit this)
├── pages/
│   ├── 1_Auth.py           # Login / Sign Up
│   └── 2_Dashboard.py      # ChatGPT-style dashboard
├── utils/
│   ├── auth_helper.py      # User auth + password validation
│   ├── csv_loader.py       # CSV → SQLite
│   ├── schema_generator.py # Schema string for LLM
│   ├── sql_executor.py     # Execute SQL on SQLite
│   ├── llm_helper.py       # Gemini API (schema-only, no user data)
│   └── chart_generator.py  # Plotly chart builder
├── database/               # SQLite database (auto-created)
└── data/                   # Uploaded CSVs (auto-created)
```
