import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_system_prompt():
    """Reads the system prompt from the system_prompt.md file."""
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "system_prompt.md")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful AI assistant."

def clean_json_response(response_text):
    """
    Cleans the markdown formatting or raw text returned by the LLM
    to extract valid JSON.
    """
    # Remove markdown code block syntax if present
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Try to find JSON-like structure
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1:
            json_str = response_text[start:end+1]
        else:
            json_str = response_text

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON from LLM response.", "raw_response": response_text}

def generate_sql_query(user_prompt: str, schema: str, table_name: str = "dataset"):
    """
    Calls Gemini API with the system prompt, dataset schema, and user question.
    Only sends the schema, never the user data.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY is not set in the .env file."}

    genai.configure(api_key=api_key)
    
    # We use gemini-1.5-flash for speed and reliability in prototyping
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    system_prompt = get_system_prompt()
    
    full_prompt = (
        f"{system_prompt}\n\n"
        f"Here is the database context:\n"
        f"{schema}\n\n"
        f"Table Name: {table_name}\n\n"
        f"User Question: {user_prompt}\n\n"
        f"Respond ONLY with the requested JSON format."
    )
    
    try:
        # Optional: you could add generation config for strict JSON schema output if supported, 
        # but parsing is usually sufficient for prototypes.
        response = model.generate_content(full_prompt)
        return clean_json_response(response.text)
    except Exception as e:
        return {"error": f"LLM Error: {str(e)}"}
