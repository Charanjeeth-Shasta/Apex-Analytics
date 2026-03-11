import plotly.express as px
import pandas as pd

# Vibrant color palette — prevents all-blue charts
PALETTE = [
    "#7c3aed", "#f59e0b", "#10b981", "#ef4444", "#3b82f6",
    "#ec4899", "#14b8a6", "#f97316", "#8b5cf6", "#06b6d4"
]

LAYOUT_DEFAULTS = dict(
    template="plotly_white",
    margin=dict(l=20, r=20, t=50, b=20),
    font=dict(family="Inter, sans-serif", size=13),
    plot_bgcolor="#f9fafb",
    paper_bgcolor="#ffffff",
    colorway=PALETTE,
)

def _fmt(col: str) -> str:
    return col.replace("_", " ").title()

def generate_chart(data: list, chart_config: dict):
    """
    Generates a Plotly chart based on the data and configuration.
    Returns a Plotly Figure or None.
    """
    if not data:
        return None

    df = pd.DataFrame(data)

    chart_type = chart_config.get("chart_type", "").lower()
    x_axis = chart_config.get("x_axis")
    y_axis = chart_config.get("y_axis")

    # Fallback x axis
    if x_axis not in df.columns:
        text_cols = df.select_dtypes(include=["object"]).columns
        x_axis = text_cols[0] if len(text_cols) > 0 else (df.columns[0] if len(df.columns) > 0 else None)

    # Fallback y axis
    if y_axis not in df.columns:
        num_cols = df.select_dtypes(include=["number"]).columns
        y_axis = num_cols[0] if len(num_cols) > 0 else (df.columns[1] if len(df.columns) > 1 else None)

    if x_axis is None or y_axis is None:
        return None

    try:
        if chart_type == "bar":
            fig = px.bar(
                df, x=x_axis, y=y_axis,
                title=f"{_fmt(y_axis)} by {_fmt(x_axis)}",
                color=x_axis,
                color_discrete_sequence=PALETTE,
            )
        elif chart_type == "line":
            fig = px.line(
                df, x=x_axis, y=y_axis,
                title=f"{_fmt(y_axis)} over {_fmt(x_axis)}",
                color_discrete_sequence=PALETTE,
                markers=True,
            )
        elif chart_type == "pie":
            fig = px.pie(
                df, names=x_axis, values=y_axis,
                title=f"{_fmt(y_axis)} Distribution",
                color_discrete_sequence=PALETTE,
                hole=0.35,
            )
        elif chart_type == "histogram":
            fig = px.histogram(
                df, x=x_axis,
                title=f"Distribution of {_fmt(x_axis)}",
                color_discrete_sequence=[PALETTE[0]],
            )
        elif chart_type == "scatter":
            fig = px.scatter(
                df, x=x_axis, y=y_axis,
                title=f"{_fmt(y_axis)} vs {_fmt(x_axis)}",
                color=x_axis if df[x_axis].dtype == object else None,
                color_discrete_sequence=PALETTE,
            )
        else:
            fig = px.bar(
                df, x=x_axis, y=y_axis,
                title=f"{_fmt(y_axis)} by {_fmt(x_axis)}",
                color=x_axis,
                color_discrete_sequence=PALETTE,
            )

        fig.update_layout(
            xaxis_title=_fmt(x_axis),
            yaxis_title=_fmt(y_axis) if chart_type != "pie" else None,
            **LAYOUT_DEFAULTS,
        )
        return fig
    except Exception as e:
        print(f"Failed to generate chart: {e}")
        return None
