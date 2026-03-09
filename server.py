import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import backend utility modules
from utils.csv_loader import load_csv_to_sqlite
from utils.schema_generator import generate_schema
from utils.llm_helper import generate_sql_query
from utils.sql_executor import run_query

app = Flask(__name__)
# Enable CORS for Streamlit frontend access
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join("data")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # 50 MB limit

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles CSV file uploads.
    Saves the file to disk, loads it into SQLite, and returns the schema.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file to disk securely
        file.save(filepath)
        
        try:
            # Load the CSV into SQLite (dataframe is deleted internally)
            load_csv_to_sqlite(filepath, table_name="dataset")
            
            # Generate the new schema to verify
            schema = generate_schema(table_name="dataset")
            
            return jsonify({
                "message": f"Successfully uploaded {filename} and loaded to database.",
                "schema": schema,
                "status": "success"
            }), 200
        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
            
    return jsonify({"error": "Invalid file type. Only CSV allowed."}), 400

@app.route('/query', methods=['POST'])
def process_query():
    """
    Accepts a natural language query from the frontend.
    Generates the SQL using LLM, executes the SQL, and returns data and chart config.
    """
    data = request.json
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400
        
    user_prompt = data['prompt']
    
    # Generate the current schema description from SQLite
    schema = generate_schema("dataset")
    if "Error" in schema or "No columns" in schema:
         return jsonify({"error": "Database schema error. Please upload a valid dataset first."}), 400
         
    # Generate SQL and chart config from Gemini LLM
    llm_response = generate_sql_query(user_prompt, schema, "dataset")
    
    # Check for direct LLM errors
    if "error" in llm_response:
        return jsonify(llm_response), 400
        
    sql_query = llm_response.get("sql_query")
    if not sql_query:
         return jsonify({"error": "Failed to generate a valid SQL query."}), 500
         
    # Execute the generated SQL safely on SQLite
    query_result = run_query(sql_query)
    
    if query_result.get("error"):
         return jsonify({
             "error": "Failed to execute generated SQL.",
             "sql_error": query_result["error"],
             "generated_sql": sql_query,
             "llm_explanation": llm_response.get("explanation", "")
         }), 400
         
    # Package final response for the frontend
    response_payload = {
        "status": "success",
        "data": query_result["data"],  # Raw table data for display and charting
        "chart_config": {
            "chart_type": llm_response.get("chart_type"),
            "x_axis": llm_response.get("x_axis"),
            "y_axis": llm_response.get("y_axis"),
        },
        "query_details": {
            "generated_sql": sql_query,
            "explanation": llm_response.get("explanation")
        }
    }
    
    return jsonify(response_payload), 200

if __name__ == '__main__':
    # Run the Flask app on localhost:5001
    app.run(debug=True, port=5001)
