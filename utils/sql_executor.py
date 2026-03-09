import sqlite3
import os

DATABASE_PATH = os.path.join("database", "database.db")

def run_query(sql_query: str):
    """
    Executes a SQL query against the SQLite database and returns the result
    as a list of dictionaries (native Python objects).
    Does NOT use Pandas.
    """
    if not os.path.exists(DATABASE_PATH):
        return {"error": "Database not found. Please upload data first.", "data": []}
        
    # Security: rudimentary block for destructive queries
    lower_query = sql_query.lower()
    if any(keyword in lower_query for keyword in ['drop', 'insert', 'update', 'delete', 'alter']):
        return {"error": "Only SELECT queries are allowed.", "data": []}
        
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        # Use Row factory to get dict-like objects
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Convert row objects to standard dicts
        result_data = [dict(row) for row in rows]
        
        conn.close()
        return {"error": None, "data": result_data}
        
    except sqlite3.Error as e:
        return {"error": str(e), "data": []}
    except Exception as e:
        return {"error": str(e), "data": []}
