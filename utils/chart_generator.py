import plotly.express as px
import pandas as pd

def generate_chart(data: list, chart_config: dict):
    """
    Generates a Plotly chart based on the data and configuration.
    
    Args:
        data: A list of dictionaries representing the query result.
        chart_config: A dictionary containing chart_type, x_axis, and y_axis.
        
    Returns:
        Plotly Figure object or None if generation fails/is inappropriate.
    """
    if not data or len(data) == 0:
        return None
        
    df = pd.DataFrame(data)
    
    chart_type = chart_config.get("chart_type", "").lower()
    x_axis = chart_config.get("x_axis")
    y_axis = chart_config.get("y_axis")
    
    # We require at least columns defined or default fallback
    if x_axis not in df.columns:
        # Fallback to first text column
        text_cols = df.select_dtypes(include=['object']).columns
        if len(text_cols) > 0:
             x_axis = text_cols[0]
        elif len(df.columns) > 0:
             x_axis = df.columns[0]
        else:
             return None
             
    if y_axis not in df.columns:
        # Fallback to first numeric column for y_axis
        num_cols = df.select_dtypes(include=['number']).columns
        if len(num_cols) > 0:
             y_axis = num_cols[0]
        elif len(df.columns) > 1:
             y_axis = df.columns[1]
        else:
             return None

    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
        elif chart_type == "line":
            # For lines, ensure it handles unsorted data if x_axis is time/ordered
            fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
        elif chart_type == "pie":
            fig = px.pie(df, names=x_axis, values=y_axis, title=f"{y_axis} Distribution")
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_axis, title=f"Distribution of {x_axis}")
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
        else:
            # Default to bar chart if unknown
            fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
            
        fig.update_layout(
             xaxis_title=x_axis.replace('_', ' ').title(),
             yaxis_title=y_axis.replace('_', ' ').title(),
             template="plotly_dark", # Or your preferred cool theme
             margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
    except Exception as e:
        print(f"Failed to generate chart: {e}")
        return None
