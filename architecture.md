# architecture.md

## Conversational AI for Instant Business Intelligence Dashboards

---

# 1. System Overview

This application allows users to:

1. Upload a CSV dataset
2. Ask questions in natural language
3. Automatically generate SQL queries using an LLM
4. Query the dataset
5. Generate interactive dashboards

The system converts **text → SQL → data → visualization**.

Primary design goals:

* Simplicity
* Fast prototyping
* Clean architecture
* Easy deployment

The entire system runs as a **single Streamlit web application with modular Python components**.

---

# 2. High-Level Architecture

System pipeline:

```
User Prompt
      ↓
Streamlit Interface
      ↓
Prompt Processing Layer
      ↓
Gemini API
(NL → SQL + Chart Type)
      ↓
SQLite Query Engine
      ↓
Pandas DataFrame
      ↓
Chart Generator (Plotly)
      ↓
Interactive Dashboard
```

---

# 3. Application Layers

The project is divided into **five logical layers**.

### 1. UI Layer

Responsible for:

* CSV upload
* prompt input
* displaying dashboards
* showing query results

Implemented using **Streamlit**.

---

### 2. Data Processing Layer

Responsible for:

* loading CSV files
* cleaning data
* converting datasets into SQLite tables

Uses:

* Pandas
* SQLite

---

### 3. LLM Processing Layer

Responsible for:

* sending prompts to Gemini
* generating SQL queries
* recommending chart types

Input:

```
User question
Dataset schema
System prompt
```

Output:

```
SQL query
Chart type
X-axis
Y-axis
```

---

### 4. Query Execution Layer

Responsible for:

* executing generated SQL queries
* retrieving data from SQLite

Returns:

```
Pandas DataFrame
```

---

### 5. Visualization Layer

Responsible for:

* selecting visualization types
* rendering interactive charts

Uses:

* Plotly

---

# 4. Project Folder Structure

The project should follow this structure:

```
conversational-bi-dashboard/

│
├── app.py
│
├── requirements.txt
│
├── program.md
├── system_prompt.md
├── architecture.md
│
├── data/
│   └── sample_sales.csv
│
├── utils/
│   ├── csv_loader.py
│   ├── schema_generator.py
│   ├── llm_helper.py
│   ├── sql_executor.py
│   ├── chart_generator.py
│
└── database/
    └── database.db
```

---

# 5. File Responsibilities

---

# app.py

Main Streamlit application.

Responsibilities:

* render UI
* handle file uploads
* capture user prompts
* call backend modules
* render charts

Key UI elements:

```
Title: Conversational BI Dashboard

File Upload Component
Text Input for Query
Generate Dashboard Button
Chart Display Area
Query Results Table
```

Workflow:

```
Upload CSV
    ↓
Store in SQLite
    ↓
User enters query
    ↓
Send to LLM
    ↓
Receive SQL + chart
    ↓
Execute SQL
    ↓
Generate chart
    ↓
Display dashboard
```

---

# utils/csv_loader.py

Responsible for loading CSV files.

Functions:

```
load_csv(file)
save_to_sqlite(dataframe, table_name)
```

Example workflow:

```
CSV file → Pandas DataFrame → SQLite table
```

---

# utils/schema_generator.py

Generates dataset schema for the LLM.

Example output:

```
Table: dataset

Columns:
date (datetime)
region (text)
product (text)
revenue (float)
```

Function:

```
generate_schema(dataframe)
```

This schema is sent to the LLM.

---

# utils/llm_helper.py

Handles communication with the LLM.

Responsibilities:

* send prompt to Gemini
* include system prompt
* parse JSON response

Function:

```
generate_sql_query(user_prompt, schema)
```

Expected output:

```
{
 "sql_query": "...",
 "chart_type": "...",
 "x_axis": "...",
 "y_axis": "...",
 "explanation": "..."
}
```

---

# utils/sql_executor.py

Responsible for executing SQL queries.

Functions:

```
run_query(sql_query)
```

Output:

```
Pandas DataFrame
```

---

# utils/chart_generator.py

Responsible for generating visualizations.

Input:

```
dataframe
chart_type
x_axis
y_axis
```

Output:

```
Plotly chart
```

Supported chart types:

```
bar
line
pie
scatter
histogram
```

---

# 6. Data Flow

Example workflow:

### Step 1

User uploads:

```
sales.csv
```

---

### Step 2

System loads dataset:

```
CSV → Pandas DataFrame
```

---

### Step 3

Dataset stored:

```
DataFrame → SQLite table
```

---

### Step 4

User prompt:

```
Show revenue by region
```

---

### Step 5

LLM processing:

Input:

```
User question
Dataset schema
System prompt
```

Output:

```
SQL query
Chart type
```

---

### Step 6

Query execution:

```
SQL → SQLite → DataFrame
```

---

### Step 7

Visualization:

```
DataFrame → Plotly chart
```

---

### Step 8

Dashboard displayed in Streamlit.

---

# 7. Error Handling

The application must handle these cases.

---

### Invalid SQL

If SQL fails:

```
Display error message
Ask user to rephrase query
```

---

### Missing Columns

If user asks about missing fields:

```
Return message listing available columns
```

---

### Empty Query Results

If query returns no rows:

```
Display "No data available for this query"
```

---

# 8. Performance Considerations

For prototype scale:

* SQLite is sufficient
* datasets expected < 50MB
* queries executed locally

Optimization ideas:

* caching dataset schema
* caching LLM responses

---

# 9. Deployment Architecture

Deployment steps:

1. Push project to GitHub
2. Deploy using Streamlit Cloud

Application runs as:

```
Streamlit Web App
```

No separate backend required.

---

# 10. Future Improvements

Potential upgrades:

### Multi-chart dashboards

Single query → multiple visualizations.

---

### Conversational memory

Allow follow-up questions:

```
Now filter for East region
```

---

### Smart insights

Automatically generate:

* summary statistics
* anomalies
* trends

---

### Multiple dataset support

Allow querying across multiple uploaded datasets.

---

# Final Architecture Summary

Core components:

```
Streamlit UI
        ↓
Gemini API
        ↓
SQLite Database
        ↓
Pandas
        ↓
Plotly Charts
```

This architecture prioritizes:

* fast development
* minimal complexity
* high demo value

---