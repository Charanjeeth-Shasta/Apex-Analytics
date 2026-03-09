# Apex Analytics

## Conversational AI for Instant Business Intelligence Dashboards

This project allows non-technical users to upload CSV data, ask plain-English questions, and instantly generate interactive BI dashboards and data views using Google Gemini LLM, Flask, and Streamlit.

### Setup Instructions

1.  **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure `.env`:**
    Add your API key to the `.env` file in the root directory:
    ```
    GEMINI_API_KEY="your_api_key_here"
    ```

3.  **Run the Backend (Flask):**
    ```bash
    python server.py
    ```

4.  **Run the Frontend (Streamlit) in a new terminal:**
    *(Because of Python 3.14 compatibility, use the custom launcher)*
    ```bash
    python run_app.py
    ```
