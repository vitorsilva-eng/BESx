import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_ems_dispatch_comparison(df: pd.DataFrame, time_col: str, limite_w: float = None):
    """
    Plots a comparison between Original Load, Adjusted Load, and Battery Power.
    Includes a reference line for the demand limit.
    """
    fig = go.Figure()
    
    # Original Load
    fig.add_trace(go.Scatter(
        x=df[time_col], y=df['Carga_W'],
        name="Carga Original (W)",
        line=dict(color='#636efa', width=2),
        opacity=0.4
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
        line=dict(color='#ff0055', dash='dot', width=1)
    ))

    # Demand Limit Reference
    if limite_w:
        fig.add_hline(
            y=limite_w, 
            line_dash="dash", 
            line_color="#ffcc00",
            annotation_text=f"Limite: {limite_w/1000:.1f} kW",
            annotation_position="top left"
        )
    
    fig.update_layout(
        title="Comparativo de Despacho EMS (Intervenção da Bateria)",
        xaxis_title="Tempo",
        yaxis_title="Potência (W)",
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=550,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    return fig

def plot_energy_balance(df: pd.DataFrame, time_col: str):
    """
    Plots the accumulated energy balance (kWh).
    Helps the user decide on battery capacity for Step 2.
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[time_col], y=df['Energia_Acumulada_kWh'],
        name="Balanço de Energia (kWh)",
        line=dict(color='#00ffcc', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title="Balanço de Energia Acumulado (kWh)",
        xaxis_title="Tempo",
        yaxis_title="Energia (kWh)",
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    
    return fig

def plot_load_duration_curve(df: pd.DataFrame, load_col: str = 'Carga_W'):
    """
    Plots the Load Duration Curve (LDC).
    Shows how much time (in %) the load stays above a certain value.
    """
    # Sort values descending
    sorted_load = np.sort(df[load_col].values)[::-1]
    
    # Calculate percentage (0 to 100%)
    percentage = np.linspace(0, 100, len(sorted_load))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=percentage, y=sorted_load,
        name="Carga Ordenada",
        fill='tozeroy',
        line=dict(color='#ffcc00', width=2)
    ))
    
    fig.update_layout(
        title="Curva de Permanência de Carga (Load Duration Curve)",
        xaxis_title="Tempo (%)",
        yaxis_title="Potência (W)",
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def plot_load_frequency_histogram(df: pd.DataFrame, load_col: str = 'Carga_W', bins: int = 15):
    """
    Plots a Frequency Histogram of the Load.
    Shows the percentage of time the load stays within specific power ranges.
    """
    # Convert to kW for better labeling if values are large
    load_data = df[load_col].values
    is_kw = load_data.max() > 10000 # Rough heuristic
    
    if is_kw:
        load_data = load_data / 1000.0
        unit = "kW"
    else:
        unit = "W"
    
    counts, bin_edges = np.histogram(load_data, bins=bins)
    
    # Calculate percentage of total time
    pct_counts = (counts / len(load_data)) * 100
    
    # Create bin labels: "0-10"
    bin_labels = [f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(len(bin_edges)-1)]
    
    fig = go.Figure(data=[
        go.Bar(
            x=bin_labels,
            y=pct_counts,
            marker_color='#ffcc00',
            text=[f"{v:.1f}%" if v > 1 else "" for v in pct_counts],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Histograma de Frequência de Carga (Distribuição de Tempo)",
        xaxis_title=f"Faixa de Potência ({unit})",
        yaxis_title="Tempo Total (%)",
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def plot_load_heatmap(df: pd.DataFrame, time_col: str, load_col: str = 'Carga_W'):
    """
    Plots a Heatmap of Hour vs Day of Week.
    Helps identify operational patterns (shifts, weekends).
    """
    df_temp = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_temp[time_col]):
        df_temp[time_col] = pd.to_datetime(df_temp[time_col])
        
    df_temp['Hour'] = df_temp[time_col].dt.hour
    df_temp['Weekday'] = df_temp[time_col].dt.day_name()
    df_temp['DayNum'] = df_temp[time_col].dt.dayofweek # 0=Mon, 6=Sun
    
    # Create a pivot table Mean Power
    pivot = df_temp.pivot_table(
        index='Hour', 
        columns=['DayNum', 'Weekday'], 
        values=load_col, 
        aggfunc='mean'
    ).sort_index(axis=1) # Sort by DayNum
    
    # Extract labels for X-axis (only the name)
    # pivot.columns is a MultiIndex [(0, 'Monday'), (1, 'Tuesday')...]
    x_labels = [c[1] for c in pivot.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=x_labels,
        y=pivot.index,
        colorscale='Viridis',
        colorbar=dict(title='Watts')
    ))
    
    fig.update_layout(
        title="Padrão de Consumo Médio (Hora x Dia da Semana)",
        xaxis_title="Dia da Semana",
        yaxis_title="Hora do Dia",
        template="plotly_dark",
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Reverse Y axis so 0h is at top or keep standard? 
    # Usually engineers like 0h at the top (top-down view of the day)
    fig.update_yaxes(autorange='reversed')
    
    return fig

def plot_peak_analysis(energy_ponta_kwh: float, energy_fora_ponta_kwh: float):
    """
    Simple bar chart comparing Peak vs Off-Peak energy consumption.
    """
    categories = ['Ponta', 'Fora Ponta']
    values = [energy_ponta_kwh, energy_fora_ponta_kwh]
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories, 
            y=values,
            marker_color=['#ff0055', '#00ffcc'],
            text=[f"{v:.1f} kWh" for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Distribuição de Energia (Ponta vs. Fora Ponta)",
        yaxis_title="Energia (kWh)",
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig
