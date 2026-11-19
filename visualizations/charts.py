import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

DEFAULT_TEMPLATE = "plotly_dark"

def apply_theme(fig: go.Figure) -> go.Figure:
    """Applies the custom OmniMetrics dark theme to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="#161b2b",  # Matches --bg-surface-low
        plot_bgcolor="#161b2b",
        font=dict(color="#dee1f9", family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor="#273449", zerolinecolor="#374763"),
        yaxis=dict(showgrid=True, gridcolor="#273449", zerolinecolor="#374763"),
        colorway=["#6366f1", "#5de6ff", "#45dfa4", "#ffb4ab", "#8083ff", "#a2eeff", "#fbbf24"]
    )
    return fig

def plot_histogram(df: pd.DataFrame, x_col: str, color_col: str = None) -> go.Figure:
    fig = px.histogram(df, x=x_col, color=color_col, marginal="box", template=DEFAULT_TEMPLATE)
    return apply_theme(fig)

def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None) -> go.Figure:
    fig = px.scatter(df, x=x_col, y=y_col, color=color_col, template=DEFAULT_TEMPLATE)
    return apply_theme(fig)

def plot_box(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None) -> go.Figure:
    fig = px.box(df, x=x_col, y=y_col, color=color_col, template=DEFAULT_TEMPLATE)
    return apply_theme(fig)

def plot_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    numeric_df = df.select_dtypes(include=['number'])
    if numeric_df.empty:
        return go.Figure()
    corr = numeric_df.corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", template=DEFAULT_TEMPLATE, color_continuous_scale="RdBu_r")
    return apply_theme(fig)

def plot_bar(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None) -> go.Figure:
    fig = px.bar(df, x=x_col, y=y_col, color=color_col, template=DEFAULT_TEMPLATE)
    return apply_theme(fig)

def plot_pie(df: pd.DataFrame, names_col: str, values_col: str = None) -> go.Figure:
    if values_col:
        fig = px.pie(df, names=names_col, values=values_col, template=DEFAULT_TEMPLATE)
    else:
        counts = df[names_col].value_counts().reset_index()
        counts.columns = [names_col, 'count']
        fig = px.pie(counts, names=names_col, values='count', template=DEFAULT_TEMPLATE)
    return apply_theme(fig)

def plot_line(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None) -> go.Figure:
    fig = px.line(df, x=x_col, y=y_col, color=color_col, template=DEFAULT_TEMPLATE)
    return apply_theme(fig)

def plot_violin(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None) -> go.Figure:
    fig = px.violin(df, x=x_col, y=y_col, color=color_col, box=True, template=DEFAULT_TEMPLATE)
    return apply_theme(fig)
    
def plot_3d_scatter(df: pd.DataFrame, x_col: str, y_col: str, z_col: str, color_col: str = None) -> go.Figure:
    fig = px.scatter_3d(df, x=x_col, y=y_col, z=z_col, color=color_col, template=DEFAULT_TEMPLATE)
    return apply_theme(fig)
