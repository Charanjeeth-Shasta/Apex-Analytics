import os
import uuid
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename

from utils.csv_loader import load_csv_to_sqlite
from utils.schema_generator import generate_schema
from utils.llm_helper import generate_sql_query
from utils.sql_executor import run_query
from utils.auth_helper import init_users_db, register_user, verify_user

app = Flask(__name__)
app.secret_key = os.urandom(24)  # for session management
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = os.path.join("data")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = {'csv'}

# Initialise users table on startup
init_users_db()

# chat_id → internal SQLite table name
# chat_id is generated fresh on each upload (never the auth token)
_chat_tables: dict = {}

# The table name the LLM always sees (never changes)
LLM_TABLE_ALIAS = "dataset"


def _internal_table(chat_id: str) -> str:
    """Returns a safe SQLite table identifier for a given chat_id."""
    return "chat_" + chat_id.replace("-", "")[:24]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─────────────────────────────────────────
# Auth endpoints
# ─────────────────────────────────────────

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    success, message = register_user(username, password)
    return jsonify({"success": success, "message": message}), (200 if success else 400)


@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    success, message = verify_user(username, password)
    if success:
        token = str(uuid.uuid4())
        return jsonify({"success": True, "message": message, "token": token, "username": username.lower()}), 200
    return jsonify({"success": False, "message": message}), 401


# ─────────────────────────────────────────
# Data upload endpoint
# ─────────────────────────────────────────

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # chat_id is generated fresh by the frontend for every new upload
    chat_id = request.form.get('chat_id', str(uuid.uuid4()))
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only CSV allowed."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    internal_table = _internal_table(chat_id)
    try:
        load_csv_to_sqlite(filepath, table_name=internal_table)
        _chat_tables[chat_id] = internal_table

        # Schema is generated with the real table, but we relabel it for display
        schema = generate_schema(table_name=internal_table)
        # Replace internal table name with the friendly alias for display
        schema_display = schema.replace(f"Table: {internal_table}", "Table: dataset")

        return jsonify({
            "message": f"Uploaded {filename} successfully.",
            "schema": schema_display,
            "status": "success",
            "chat_id": chat_id          # return so frontend can store it
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500


# ─────────────────────────────────────────
# Chat / Query endpoint (multi-turn)
# ─────────────────────────────────────────

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_prompt = data.get('prompt', '').strip()
    chat_id     = data.get('chat_id', '')

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    internal_table = _chat_tables.get(chat_id)
    if not internal_table:
        return jsonify({"error": "No dataset loaded for this chat. Please upload a CSV file first."}), 400

    # Generate schema using the internal table, but tell the LLM it's called 'dataset'
    raw_schema = generate_schema(internal_table)
    if "Error" in raw_schema or "No columns" in raw_schema:
        return jsonify({"error": "Schema error. Please re-upload your dataset."}), 400

    llm_schema = raw_schema.replace(f"Table: {internal_table}", f"Table: {LLM_TABLE_ALIAS}")

    # LLM receives schema with 'dataset' as the table name
    llm_response = generate_sql_query(user_prompt, llm_schema, LLM_TABLE_ALIAS)

    if "error" in llm_response:
        return jsonify(llm_response), 400

    # LLM is asking for clarification — return the question to the frontend
    if llm_response.get("clarification_needed"):
        return jsonify({
            "status": "clarification",
            "question": llm_response.get("question", "Could you please clarify your question?")
        }), 200

    sql_query = llm_response.get("sql_query")
    if not sql_query:
        return jsonify({"error": "Failed to generate a valid SQL query."}), 500

    # Substitute 'dataset' → actual internal table name before execution
    import re as _re
    safe_sql = _re.sub(
        r'\bdataset\b', internal_table, sql_query, flags=_re.IGNORECASE
    )

    query_result = run_query(safe_sql)

    if query_result.get("error"):
        return jsonify({
            "error": "Failed to execute generated SQL.",
            "sql_error": query_result["error"],
            "generated_sql": sql_query,
            "llm_explanation": llm_response.get("explanation", "")
        }), 400

    return jsonify({
        "status": "success",
        "data": query_result["data"],
        "chart_config": {
            "chart_type": llm_response.get("chart_type"),
            "x_axis":     llm_response.get("x_axis"),
            "y_axis":     llm_response.get("y_axis"),
        },
        "query_details": {
            # Show user the clean SQL (with 'dataset') not internal table name
            "generated_sql": sql_query,
            "explanation": llm_response.get("explanation")
        }
    }), 200


# ─────────────────────────────────────────
# Keep legacy /query endpoint as alias
# ─────────────────────────────────────────

@app.route('/query', methods=['POST'])
def query():
    return chat()


if __name__ == '__main__':
    app.run(debug=True, port=5001)
