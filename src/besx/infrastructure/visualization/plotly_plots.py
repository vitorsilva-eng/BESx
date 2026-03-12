import plotly.graph_objects as go
import pandas as pd

def plot_ems_dispatch_comparison(df: pd.DataFrame, time_col: str):
    """
    Plots a comparison between Original Load, Adjusted Load, and Battery Power.
    """
    fig = go.Figure()
    
    # Original Load
    fig.add_trace(go.Scatter(
        x=df[time_col], y=df['Carga_W'],
        name="Carga Original (W)",
        line=dict(color='#636efa', width=2),
        opacity=0.5
    ))
    
    # Adjusted Load
    fig.add_trace(go.Scatter(
        x=df[time_col], y=df['Carga_Ajustada_W'],
        name="Carga com Bateria (W)",
        line=dict(color='#00ffcc', width=3)
    ))
    
    # Battery Power
    fig.add_trace(go.Scatter(
        x=df[time_col], y=df['Potencia_Bateria_W'],
        name="Potência Bateria (W)",
        fill='tozeroy',
        line=dict(color='#ef553b', dash='dot')
    ))
    
    fig.update_layout(
        title="Comparativo de Despacho EMS",
        xaxis_title="Tempo",
        yaxis_title="Potência (W)",
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def plot_heuristic_soc(df: pd.DataFrame, time_col: str):
    """
    Plots the heuristically estimated SOC curve.
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[time_col], y=df['SOC_Heuristico'],
        name="SOC Estimado (%)",
        line=dict(color='#00ffcc', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title="Curva de SOC Estimada (Heurística)",
        xaxis_title="Tempo",
        yaxis_title="SOC (%)",
        yaxis=dict(range=[0, 105]),
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig
