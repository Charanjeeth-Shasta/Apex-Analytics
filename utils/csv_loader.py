import pandas as pd
import sqlite3
import os
import re

DATABASE_PATH = os.path.join("database", "database.db")

def clean_column_names(columns):
    """
    Cleans column names to be valid SQLite identifiers.
    Replaces spaces and invalid characters with underscores.
    """
    cleaned = []
    for col in columns:
        # Convert to string, lowercase, replace spaces with underscores
        c = str(col).lower().strip()
        # Remove any character that isn't alphanumeric or underscore
        c = re.sub(r'[^a-z0-9_]', '_', c)
        # Ensure it doesn't start with a number
        if c and c[0].isdigit():
            c = "col_" + c
        cleaned.append(c)
    return cleaned

def load_csv_to_sqlite(file_path: str, table_name: str = "dataset"):
    """
    Reads a CSV file into a Pandas DataFrame, cleans columns, 
    saves it to an SQLite database, and then deletes the DataFrame.
    """
    # Ensure database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Read CSV with robust encoding handling to support Excel/Windows generated files
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            # Common fallback for Excel-generated CSVs
            df = pd.read_csv(file_path, encoding='windows-1252')
        except UnicodeDecodeError:
            # Last resort: replace any unreadable characters
            df = pd.read_csv(file_path, encoding='utf-8', encoding_errors='replace')
    
    # Clean column names
    df.columns = clean_column_names(df.columns)
    
    # Save to SQLite
    conn = sqlite3.connect(DATABASE_PATH)
    # Replace the table if it already exists (useful for uploading a new dataset)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    
    # Explicitly delete the DataFrame from memory as requested
    del df
    
    return True
