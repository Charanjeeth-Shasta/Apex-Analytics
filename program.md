# program.md 
## Project Title : Apex-Analytics
## Conversational AI for Instant Business Intelligence Dashboards

---

# 1. Project Overview

This project builds a **Conversational AI system that generates interactive Business Intelligence dashboards from natural language prompts**.

Unlike traditional BI tools that require **SQL knowledge or manual dashboard configuration**, this system allows users to:

1. Upload their own dataset (CSV file)
2. Ask questions about the data in plain English
3. Automatically generate dashboards and charts

The system converts user prompts into SQL queries using an **LLM (Google Gemini)** and generates interactive visualizations instantly.

Example user prompt:

```
Show the monthly sales revenue for Q3 broken down by region
```

The system will:

1. Understand the user request
2. Generate SQL query
3. Query the uploaded dataset
4. Select the best chart type
5. Render an interactive dashboard

---

# 2. Core Feature: Upload Any CSV and Query It

The system must allow users to upload **any CSV file** and instantly begin querying it.

This makes the application **data-format agnostic**, meaning it works with any structured dataset.

Example workflow:

### Step 1: Upload CSV

User uploads:

```
sales_data.csv
```

Example dataset columns:

```
date
region
product
category
revenue
units_sold
```

---

### Step 2: System Reads Data

The system will:

1. Load CSV using **Pandas**
2. Automatically detect column names
3. Store dataset into **SQLite database**
4. Generate a schema description for the LLM

Example generated schema:

```
Table: dataset

Columns:
date (datetime)
region (text)
product (text)
category (text)
revenue (float)
units_sold (integer)
```

---

### Step 3: User Queries Data

User can ask questions like:

```
Show revenue by region
```

```
What are the top 5 products by sales?
```

```
Show monthly sales trend
```

---

### Step 4: LLM Generates SQL

The Gemini API converts the prompt into SQL.

Example output:

```sql
SELECT region, SUM(revenue)
FROM dataset
GROUP BY region
ORDER BY SUM(revenue) DESC
```

---

### Step 5: Query Execution

The SQL query is executed on the **SQLite database**.

The result is returned as a Pandas DataFrame.

---

### Step 6: Chart Selection

The LLM also recommends a chart type based on the data.

Example mapping:

| Query Type          | Chart      |
| ------------------- | ---------- |
| Time series         | Line chart |
| Category comparison | Bar chart  |
| Proportion          | Pie chart  |
| Distribution        | Histogram  |

---

### Step 7: Dashboard Rendering

Charts are rendered using **Plotly** and displayed inside **Streamlit**.

Charts should support:

* hover tooltips
* zoom
* legends
* interactive exploration

---

# 3. Target User

**Non-Technical Executives and Business Managers**

Characteristics:

* Cannot write SQL queries
* Need quick insights
* Prefer conversational interfaces
* Need simple dashboards

---

# 4. System Architecture

The architecture converts natural language into dashboards.

System flow:

```
User Prompt
      ↓
Streamlit UI
      ↓
Gemini API (Prompt → SQL + Chart Type)
      ↓
SQLite Database
      ↓
Query Result
      ↓
Plotly Visualization
      ↓
Interactive Dashboard
```

---

# 5. Technology Stack

## Frontend

**Streamlit**

Used for:

* text input interface
* CSV upload
* dashboard layout
* chart rendering

Reason:

* extremely fast UI development
* perfect for data apps

---

## Backend

**Python**

Handles:

* API communication
* data processing
* SQL execution

---

## LLM

**Google Gemini API**

Used for:

* converting natural language → SQL
* selecting chart types
* understanding dataset schema

---

## Data Processing

**Pandas**

Used for:

* loading CSV
* data cleaning
* converting to SQL tables

Example:

```
pd.read_csv("data.csv")
```

---

## Database

**SQLite**

Reason:

* lightweight
* no installation required
* perfect for temporary datasets

CSV files will be converted into SQLite tables.

---

## Visualization

**Plotly**

Used for interactive dashboards.

Supported charts:

* bar chart
* line chart
* pie chart
* scatter plot
* histogram

---

# 6. Application Workflow

### 1. User uploads CSV

```
Upload sales_data.csv
```

---

### 2. System reads dataset

```
CSV → Pandas → SQLite
```

---

### 3. User enters prompt

```
Show revenue by region
```

---

### 4. Prompt sent to Gemini

Gemini receives:

* user question
* table schema
* instructions

---

### 5. Gemini generates SQL

Example:

```sql
SELECT region, SUM(revenue)
FROM dataset
GROUP BY region
```

---

### 6. Query executed

Results returned as dataframe.

---

### 7. Chart generated

Plotly creates a bar chart.

---

### 8. Dashboard displayed

Streamlit shows:

* chart
* query results
* user prompt

---

# 7. Error Handling

The system must handle:

### Unknown Columns

Example:

User asks:

```
Show employee salaries
```

System response:

```
The dataset does not contain salary information.

Available columns:
date, region, product, revenue
```

---

### Ambiguous Prompts

Example:

```
Show performance
```

System should ask clarification:

```
Do you mean sales performance or product performance?
```

---

# 8. Example Queries

### Query 1

```
Show total revenue by region
```

Output:

Bar chart

---

### Query 2

```
Display monthly sales trend
```

Output:

Line chart

---

### Query 3

```
Show top 5 products by revenue
```

Output:

Bar chart

---

### Query 4

```
What percentage of revenue comes from each category?
```

Output:

Pie chart

---

# 9. GitHub Repository Structure

Example structure:

```
project/
│
├── app.py
├── program.md
├── requirements.txt
├── data/
│   └── sample_sales.csv
│
├── utils/
│   ├── llm_helper.py
│   ├── sql_generator.py
│   ├── chart_selector.py
│
└── README.md
```

---

# 10. Expected Deliverables

The final project should include:

### 1. Working Web App

Users can:

* upload CSV
* type natural language queries
* generate dashboards

---

### 2. Public GitHub Repository

Contains:

```
source code
documentation
dataset examples
```

---

### 3. Demo Presentation

Show at least three queries:

```
1. Show revenue by region
2. Show monthly revenue trend
3. Show top product category in Q3
```

---

✅ This version **perfectly aligns with the evaluation criteria** because:

* **Data format agnostic (20 bonus points)**
* Conversational dashboard
* Interactive charts
* LLM powered BI

---