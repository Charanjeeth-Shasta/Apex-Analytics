import sqlite3
import os

DATABASE_PATH = os.path.join("database", "database.db")

def generate_schema(table_name="dataset"):
    """
    Connects to the SQLite database and generates a schema definition
    string formatting for the LLM.
    """
    if not os.path.exists(DATABASE_PATH):
        return f"Table: {table_name}\n\nColumns: (No data uploaded)"
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Pragma table_info returns:
    # (cid, name, type, notnull, dflt_value, pk)
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
    except Exception as e:
        conn.close()
        return f"Error retrieving schema: {str(e)}"
        
    conn.close()
    
    if not columns_info:
        return f"Table: {table_name}\n\nColumns: (No columns found)"
        
    schema_lines = [f"Table: {table_name}", "", "Columns:"]
    for col in columns_info:
        col_name = col[1]
        # map SQLite types to simplified types
        col_type = col[2].lower()
        if "int" in col_type:
            mapped_type = "integer"
        elif "char" in col_type or "text" in col_type or "clob" in col_type:
            mapped_type = "text"
        elif "real" in col_type or "floa" in col_type or "doub" in col_type:
            mapped_type = "float"
        elif "date" in col_type or "time" in col_type:
            mapped_type = "datetime"
        else:
            mapped_type = "unknown"
            
        schema_lines.append(f"{col_name} ({mapped_type})")
        
    return "\n".join(schema_lines)
