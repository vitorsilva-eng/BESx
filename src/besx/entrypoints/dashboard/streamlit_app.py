import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import time
import os
import json
import ast

import importlib
# Internal imports
import besx.config
import besx.domain.models.degradation_model
import besx.infrastructure.plecs.plecs_connector
import besx.application.simulation

from besx.application.simulation import SimulationManager
from besx.config import CONFIGURACAO, PERFIS_BATERIA, ModeloDegradacaoConfig, BateriaConfig
from besx.domain.models.degradation_model import (
    calcular_dano_referencia_serrao, 
    calcular_fator_severidade, 
    calcular_rul
)
from besx.infrastructure.llm.gemini_analyzer import analisar_comparacao_bess

# Add tests path to sys.path if not present (to allow importing tests)
import sys
tests_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../tests'))
if tests_path not in sys.path:
    sys.path.insert(0, tests_path)

import mission_profile_generator
import test_engine_validation

def refresh_modules():
    """Recarrega os módulos do motor para refletir alterações de código sem reiniciar o Streamlit."""
    import besx.domain.models.battery_simulator
    import besx.infrastructure.plecs.plecs_connector
    import mission_profile_generator
    import test_engine_validation
    
    importlib.reload(besx.domain.models.battery_simulator)
    importlib.reload(besx.infrastructure.plecs.plecs_connector)
    importlib.reload(mission_profile_generator)
    importlib.reload(test_engine_validation)

# Page Config
st.set_page_config(
    page_title="BESx Simulation Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Theme Configuration ---
THEME_COLORS = {
    "PRIMARY": "#00ffcc",
    "SECONDARY": "#31333f",
    "DANGER": "#ff4b4b",
    "SUCCESS": "#3cba92",
    "WARNING": "#ffcc00",
    "CALENDAR": "#636efa", # Azul
    "CYCLE": "#ef553b",    # Vermelho/Laranja
    "SOH": "#00ffcc",
    "TEXT": "#e6edf3",
    "GRID": "#30363d"
}

# --- App State Management ---
if 'sim_results' not in st.session_state: st.session_state.sim_results = pd.DataFrame()
if 'curr_soc' not in st.session_state: st.session_state.curr_soc = pd.DataFrame()
if 'curr_input' not in st.session_state: st.session_state.curr_input = pd.DataFrame()
if 'sim_status' not in st.session_state: st.session_state.sim_status = "idle" # idle, running, finished
if 'validation_profiles' not in st.session_state: st.session_state.validation_profiles = {}
if 'validation_run' not in st.session_state: st.session_state.validation_run = None
if 'throughput' not in st.session_state: st.session_state.throughput = 0.0
if 'energy_charge' not in st.session_state: st.session_state.energy_charge = 0.0
if 'energy_discharge' not in st.session_state: st.session_state.energy_discharge = 0.0
if 'config_override' not in st.session_state: st.session_state.config_override = CONFIGURACAO.modelo_degradacao.model_copy(deep=True).model_dump()

# Custom CSS
st.markdown("""
<style>
    :root {
        --border-color: #30363d;
    }
    
    /* Depende do tema natural do Streamlit (transparente ou baseado no css nativo do stMetric) 
       Evitamos forçar background escuro absoluto */
    .stMetric { 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid var(--border-color);
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }

    .main { background-color: transparent; }
    
    .metric-card {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        margin-bottom: 10px;
    }
    
    div[data-testid="stSidebar"] { }
    .battery-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 5px; }
    .battery-container { width: 64px; height: 130px; border: 3px solid #4a4a5a; border-radius: 10px; position: relative; padding: 4px; background: rgba(0, 0, 0, 0.2); box-shadow: inset 0 2px 10px rgba(0,0,0,0.5), 0 4px 12px rgba(0,0,0,0.2); justify-content: flex-end; display: flex; flex-direction: column; }
    .battery-cap { width: 24px; height: 10px; background-color: #4a4a5a; position: absolute; top: -11px; left: 50%; transform: translateX(-50%); border-top-left-radius: 5px; border-top-right-radius: 5px; }
    .battery-fill { width: 100%; border-radius: 5px; height: 0%; transition: height 0.8s cubic-bezier(0.34, 1.56, 0.64, 1); position: relative; }
    .battery-fill::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0.1) 100%); border-radius: 5px; }
    .soh-text { font-weight: 800; font-size: 20px; margin-top: 15px; text-shadow: 0 2px 5px rgba(0,0,0,0.3); letter-spacing: 0.5px; }
    .soh-label { font-size: 12px; color: #a0a0b0; text-transform: uppercase; letter-spacing: 1.5px; margin-top: -2px; }
    
    /* Animation for simulation running */
    @keyframes pulse-red {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }
    .pulse-icon {
        display: inline-block;
        animation: pulse-red 1.5s infinite ease-in-out;
        color: #ffcc00;
        font-size: 24px;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

def format_sim_name(sim_id):
    """
    Formata o nome da simulação para exibição nos menus suspensos do Dashboard.
    Padrão: [BACKEND] Bateria | X meses | DD/MM/AAAA HH:MM:SS
    """
    res_path = "Results"
    import glob
    snap_pattern = os.path.join(res_path, sim_id, "data", "config_snapshot*.json")
    snap_files = glob.glob(snap_pattern)
    
    if snap_files:
        try:
            with open(snap_files[0], 'r', encoding='utf-8') as f:
                snap = json.load(f)
            
            backend = str(snap.get('backend', 'N/A')).upper()
            bateria = snap.get('bateria_nome', 'Bateria')
            meses = snap.get('total_meses_simulados', '?')
            
            # Tentar extrair data/hora do ID da pasta (timestamp final)
            parts = sim_id.split('_')
            if len(parts) >= 2:
                # O SimManager gera: backend_Bateria_YYYYMMDD_HHMMSS
                ts_str = f"{parts[-2]}_{parts[-1]}"
                try:
                    dt = datetime.datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                    dt_f = dt.strftime("%d/%m/%Y %H:%M:%S")
                except:
                    dt_f = sim_id # Fallback
            else:
                dt_f = sim_id
                
            return f"[{backend}] {bateria} | {meses} meses | {dt_f}"
        except:
            return sim_id
    return sim_id

# --- Shared UI Components ---
def render_metrics_row(df_results, throughput_mwh, month_idx=None):
    if df_results.empty:
        return
    
    # Se month_idx for None, mostramos o estado FINAL (Resumo)
    # Se for um inteiro, mostramos os dados daquele mês específico
    if month_idx is None:
        target_data = df_results.iloc[-1]
        label_suffix = "(Final)"
    else:
        target_data = df_results.iloc[month_idx]
        label_suffix = f"(Mês {month_idx + 1})"
    
    cols1 = st.columns(4)
    cols2 = st.columns(4)
    
    # Custom Battery Visual (Sempre baseado no SOH atual/final para contexto geral)
    with cols1[0]:
        display_soh = target_data['capacidade_restante']
        fill_h = max(0, min(100, (display_soh - 80) / 20 * 100)) # Entre 80% (vazia) e 100% (cheia)

        if display_soh > 95:
            color_grad = "linear-gradient(to top, #0ba360 0%, #3cba92 100%)"
            glow = "rgba(60, 186, 146, 0.4)"
            text_color = "#3cba92"
        elif display_soh > 85:
            color_grad = "linear-gradient(to top, #f2994a 0%, #f2c94c 100%)"
            glow = "rgba(242, 201, 76, 0.4)"
            text_color = "#f2c94c"
        else:
            color_grad = "linear-gradient(to top, #cb2d3e 0%, #ef473a 100%)"
            glow = "rgba(239, 71, 58, 0.4)"
            text_color = "#ef473a"

        st.markdown(f"""
        <div class="battery-wrapper">
            <div class="battery-container">
                <div class="battery-cap"></div>
                <div class="battery-fill" style="height: {fill_h}%; background: {color_grad}; box-shadow: 0 0 15px {glow};"></div>
            </div>
            <div class="soh-text" style="color: {text_color};">{display_soh:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    cols1[1].metric(f"SOH {label_suffix}", f"{target_data['capacidade_restante']:.2f}%", 
                  f"{target_data['capacidade_restante'] - 100:.2f}%")
    
    with cols1[2]:
        if month_idx is None:
            # Visão Global: calcula o dano mensal médio de toda a simulação
            dano_mes = df_results['dano_ciclos_mes'].mean() + df_results['dano_cal_mes'].mean()
        else:
            dano_mes = target_data.get('dano_ciclos_mes', 0) + target_data.get('dano_cal_mes', 0)
            
        mod_cfg = ModeloDegradacaoConfig(**st.session_state.config_override)
        is_val = calcular_fator_severidade(dano_mes, mod_cfg)
        st.metric(f"Severidade (Is) {label_suffix}", f"{is_val:.3f}", help="Ref: Serrão et al. (25°C, 50% SOC, 10% DOD)")

    with cols1[3]:
        # RUL (Remaining Useful Life)
        if len(df_results) > 0:
            n_meses = target_data['mes']
            if n_meses > 0:
                rul_anos = calcular_rul(
                    soh_atual_perc=target_data['capacidade_restante'],
                    dano_total_acumulado=target_data.get('dano_ciclo_acum', 0) + target_data.get('dano_cal_acum', 0),
                    meses_simulados=n_meses,
                    dias_por_ano_avg=CONFIGURACAO.dados_entrada.dias_por_ano_avg
                )
                st.metric("RUL (Vida Útil)", f"{rul_anos:.1f} anos", help=f"Projeção baseada na taxa de degradação atual.")
            else:
                st.metric("RUL (Vida Útil)", "---")

    with cols2[0]:
        st.metric("Throughput (MWh)", f"{throughput_mwh:.3f}")

    with cols2[1]:
        # Carga / Descarga
        if month_idx is None:
            e_charge = st.session_state.energy_charge
            e_discharge = st.session_state.energy_discharge
        else:
            e_charge = target_data.get('Energia_Carga_kWh', 0)
            e_discharge = target_data.get('Energia_Descarga_kWh', 0)
        
        # Decide unidade (kWh ou MWh)
        if e_charge > 10000:
            st.metric(f"Energia Carga {label_suffix}", f"{e_charge/1000:.2f} MWh")
        else:
            st.metric(f"Energia Carga {label_suffix}", f"{e_charge:.1f} kWh")

    with cols2[2]:
        if e_discharge > 10000:
            st.metric(f"Energia Descarga {label_suffix}", f"{e_discharge/1000:.2f} MWh")
        else:
            st.metric(f"Energia Descarga {label_suffix}", f"{e_discharge:.1f} kWh")

    with cols2[3]:
        if month_idx is None:
            efc_total = df_results['EFC_Ciclos_Equivalentes'].sum()
            st.metric("EFC (Total)", f"{efc_total:.1f}")
        else:
            efc_mes = target_data.get('EFC_Ciclos_Equivalentes', 0)
            st.metric(f"EFC {label_suffix}", f"{efc_mes:.2f}")

def render_view_overview(df_results, df_soc_mes, month_idx=None, key_suffix=""):
    c1, c2 = st.columns(2)
    with c1:
        if month_idx is not None:
            st.subheader(f"Curva de SOC - Mês {month_idx + 1}")
            if not df_soc_mes.empty:
                # Convert SOC to % for plotting if it's in fraction
                df_plot = df_soc_mes.copy()
                if df_plot['SOC'].max() <= 1.1:
                    df_plot['SOC'] *= 100.0
                fig = px.line(df_plot, x=df_plot['Tempo']/3600, y='SOC', color_discrete_sequence=[THEME_COLORS["PRIMARY"]])
                fig.update_layout(
                    xaxis_title="Horas", yaxis_title="SOC (%)", height=400,
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
                )
                st.plotly_chart(fig, use_container_width=True, key=f"soc_chart_{key_suffix}")
            else:
                st.info("Perfil de SOC não disponível para este mês no modo visualizador.")
        else:
            st.subheader("Evolução Mensal do SOH (%)")
            if not df_results.empty:
                fig = px.line(df_results, x='mes', y='capacidade_restante', markers=True, color_discrete_sequence=[THEME_COLORS["PRIMARY"]])
                fig.add_hline(y=80, line_dash="dash", line_color=THEME_COLORS["DANGER"], annotation_text="EOL")
                fig.update_layout(
                    yaxis_range=[75, 105], height=400,
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
                )
                st.plotly_chart(fig, use_container_width=True, key=f"soh_evol_{key_suffix}")
            
    with c2:
        if month_idx is not None:
            st.subheader(f"Dano Mensal - Mês {month_idx + 1}")
            target_data = df_results.iloc[month_idx]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=['Ciclo'], y=[target_data['dano_ciclos_mes']], name='Ciclo', marker_color=THEME_COLORS["CYCLE"]))
            fig.add_trace(go.Bar(x=['Calendário'], y=[target_data['dano_cal_mes']], name='Calendário', marker_color=THEME_COLORS["CALENDAR"]))
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
            )
            st.plotly_chart(fig, use_container_width=True, key=f"damage_month_{key_suffix}")
        else:
            st.subheader("Dano Acumulado ao Longo do Tempo")
            if not df_results.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_results['mes'], y=df_results['dano_ciclo_acum'], name='Dano Ciclo', fill='tozeroy', line=dict(color=THEME_COLORS["CYCLE"])))
                fig.add_trace(go.Scatter(x=df_results['mes'], y=df_results['dano_cal_acum'], name='Dano Cal', fill='tonexty', line=dict(color=THEME_COLORS["CALENDAR"])))
                fig.update_layout(
                    height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]),
                    xaxis_title="Meses"
                )
                st.plotly_chart(fig, use_container_width=True, key=f"damage_accum_{key_suffix}")

def render_view_degradation(df_results, month_idx=None, key_suffix=""):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("DOD Médio vs Limite")
        if not df_results.empty:
            if month_idx is None:
                # Multiply by 100 for display in bar chart
                df_plot_deg = df_results.copy()
                df_plot_deg['DOD_Medio_Perc'] *= 100.0
                fig = px.bar(df_plot_deg, x='mes', y='DOD_Medio_Perc', color_discrete_sequence=[THEME_COLORS["WARNING"]])
            else:
                target_data = df_results.iloc[month_idx]
                fig = px.bar(x=[f"Mês {month_idx+1}"], y=[target_data['DOD_Medio_Perc'] * 100.0], color_discrete_sequence=[THEME_COLORS["WARNING"]])
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
            )
            st.plotly_chart(fig, use_container_width=True, key=f"dod_bar_{key_suffix}")
    with c2:
        st.subheader("Composição da Degradação")
        if not df_results.empty:
            if month_idx is None:
                # Pizza do dano TOTAL final
                last = df_results.iloc[-1]
                values = [last['dano_ciclo_acum'], last['dano_cal_acum']]
                names = ['Cíclico', 'Calendário']
            else:
                target_result = df_results.iloc[month_idx]
                values = [target_result['dano_ciclos_mes'], target_result['dano_cal_mes']]
                names = ['Cíclico', 'Calendário']
            
            fig = px.pie(values=values, names=names, hole=0.4, color_discrete_sequence=[THEME_COLORS["CYCLE"], THEME_COLORS["CALENDAR"]])
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color=THEME_COLORS["TEXT"]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                template="plotly_dark" if st.get_option("theme.base") != "light" else "plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"deg_pie_{key_suffix}")

    # Novo: Histograma de DOD (Rainflow) - Sempre visível se houver dados
    if not df_results.empty:
        all_rf_data = []
        
        # Se um mês foi selecionado, pega só ele. Se for visão global, soma tudo
        if month_idx is not None:
            raw_rf = df_results.iloc[month_idx].get('Rainflow_Cycles', [])
            if isinstance(raw_rf, str):
                try: raw_rf = ast.literal_eval(raw_rf)
                except: raw_rf = []
            if isinstance(raw_rf, list):
                all_rf_data.extend(raw_rf)
            title_rf = f"📊 Espectro de Uso (DOD Rainflow) - Mês {month_idx + 1}"
        else:
            for _, row in df_results.iterrows():
                raw_rf = row.get('Rainflow_Cycles', [])
                if isinstance(raw_rf, str):
                    try: raw_rf = ast.literal_eval(raw_rf)
                    except: raw_rf = []
                if isinstance(raw_rf, list):
                    all_rf_data.extend(raw_rf)
            title_rf = "📊 Espectro de Uso Acumulado (Todos os Meses)"
            
        if len(all_rf_data) > 0:
            st.markdown("---")
            st.subheader(title_rf)
            df_rf = pd.DataFrame(all_rf_data, columns=['DOD', 'Mean', 'Count', 'Start', 'End'])
            # Convert DOD to % if it's in fraction
            if df_rf['DOD'].max() <= 1.1:
                df_rf['DOD'] *= 100.0
            fig_rf = px.histogram(df_rf, x='DOD', y='Count', nbins=20, 
                                  labels={'DOD':'Profundidade (DOD %)', 'Count':'Ocorrências'},
                           color_discrete_sequence=[THEME_COLORS["CYCLE"]])
            fig_rf.update_layout(
                height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]),
                template="plotly_dark" if st.get_option("theme.base") != "light" else "plotly_white"
            )
            st.plotly_chart(fig_rf, use_container_width=True, key=f"dod_rf_hist_{key_suffix}")

def render_view_operational(df_results, df_soc_mes, df_input_mes, month_idx=None, key_suffix=""):
    if month_idx is None:
        st.info("Selecione um mês específico para ver a análise operacional detalhada (Mapas de Calor, C-Rate).")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"SOC vs Potência - Mês {month_idx + 1}")
        if not df_soc_mes.empty and not df_input_mes.empty:
            min_l = min(len(df_input_mes), len(df_soc_mes))
            soc_vals = df_soc_mes['SOC'].values[:min_l]
            if soc_vals.max() <= 1.1:
                soc_vals *= 100.0
            fig = px.density_heatmap(x=soc_vals, y=df_input_mes.iloc[:min_l, 1].values, 
                                    labels={'x':'SOC (%)', 'y':'Potência (kW)'}, nbinsx=30, nbinsy=30,
                                    color_continuous_scale="Viridis")
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
            )
            st.plotly_chart(fig, use_container_width=True, key=f"heatmap_{key_suffix}")
    with c2:
        st.subheader(f"C-Rate - Mês {month_idx + 1}")
        if not df_input_mes.empty:
            cap_kwh = CONFIGURACAO.bateria.capacidade_nominal_wh / 1000
            crate = np.abs(df_input_mes.iloc[:, 1].values) / cap_kwh
            fig = px.histogram(x=crate, nbins=30, labels={'x': 'C-Rate'}, color_discrete_sequence=[THEME_COLORS["PRIMARY"]])
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]),
                yaxis_title="Frequência"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"crate_hist_{key_suffix}")

# --- Sidebar ---
st.sidebar.title("🔋 BESx Dashboard")
is_running = st.session_state.sim_status == "running"

pasta_db = 'database'
arquivos_db = [f for f in os.listdir(pasta_db) if f.endswith(('.mat', '.csv'))] if os.path.exists(pasta_db) else []
data_file_sidebar = st.sidebar.selectbox("Perfil de Dados", arquivos_db if arquivos_db else ["Vazio"], disabled=is_running)
battery_prof = st.sidebar.selectbox("Bateria", list(PERFIS_BATERIA.keys()), disabled=is_running)
backend = st.sidebar.radio("Backend", ["plecs","python"], horizontal=True, disabled=is_running)

st.sidebar.markdown("---")
st.sidebar.subheader("🔋 Limites de SOC")
soc_range = st.sidebar.slider("Faixa de Operação (%)", 0, 100, (20, 80), disabled=is_running)
soc_min_val, soc_max_val = soc_range

st.sidebar.markdown("---")
st.sidebar.subheader("🌡️ Temperatura")
t_cyc = st.sidebar.slider("Temp. Ciclo (°C)", 0, 70, 35, disabled=is_running)
t_idl = st.sidebar.slider("Temp. Repouso (°C)", 0, 70, 25, disabled=is_running)
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Modo de Simulação")

tipo_duracao = st.sidebar.radio("Tipo de Duração", ["Anos", "Meses"], horizontal=True, disabled=is_running)

if tipo_duracao == "Anos":
    anos_sim = st.sidebar.slider("Anos", 1, 20, 1, disabled=is_running)
    meses_total_sim = None # Será anos_sim * 12 no manager
else:
    meses_total_sim = st.sidebar.slider("Meses", 1, 12, 6, disabled=is_running)
    anos_sim = 0 # Valor dummy, manager usará meses_total_sim

sim_eol_mode = st.sidebar.toggle("🔋 Simular até Fim de Vida (EOL)", disabled=is_running)
if sim_eol_mode:
    st.sidebar.warning("⚠️ Modo EOL ativo: a simulação ignora a duração fixa e para ao atingir o limite de capacidade.")

# Tabs
tab_live, tab_hist, tab_comp, tab_val, tab_cfg = st.tabs(["🚀 Tempo Real", "📂 Histórico", "📈 Comparativo", "✔️ Validação Engine", "⚙️ Configurações"])

# --- TAB 1: LIVE ---
with tab_live:
    # Aviso de status no topo
    msg_placeholder = st.empty()
    if st.session_state.sim_status == "running":
        msg_placeholder.markdown('<div style="text-align: center;"><span class="pulse-icon">⚡</span><b>Simulação em Andamento...</b><br><small>(Evite interagir com menus durante o processamento para não interromper)</small></div>', unsafe_allow_html=True)
    elif st.session_state.sim_status == "finished":
        msg_placeholder.success("🎉 Simulação Concluída com Sucesso!")

    # View selection
    view_set_live = st.radio("Conjunto de Visualização", 
                           ["📊 Visão Geral", "📉 Degradação", "⚡ Operacional"], 
                           horizontal=True, key="live_view", disabled=is_running)
    
    # Placeholders para atualização em tempo real
    metrics_placeholder = st.empty()
    st.markdown("---")
    
    # Seletor de Período (Selectbox) - V2
    selected_month_idx = None
    if not st.session_state.sim_results.empty:
        n_meses = len(st.session_state.sim_results)
        opcoes = ["📊 Resumo Geral"] + [f"📅 Mês {i+1}" for i in range(n_meses)]
        sel_mode = st.selectbox("Selecione o Foco da Análise", opcoes, index=0, key="live_sel", disabled=is_running)
        if sel_mode != "📊 Resumo Geral":
            selected_month_idx = int(sel_mode.split(" ")[-1]) - 1
        st.markdown("---")

    charts_placeholder = st.empty()

    def live_callback(df_soc, res_mes, df_in):
        # Update Session State
        if st.session_state.sim_results.empty:
            st.session_state.sim_results = pd.DataFrame([res_mes])
        else:
            st.session_state.sim_results = pd.concat([st.session_state.sim_results, pd.DataFrame([res_mes])], ignore_index=True)
        
        st.session_state.curr_soc = df_soc
        st.session_state.curr_input = df_in
        cap_mwh = CONFIGURACAO.bateria.capacidade_nominal_wh / 1e6
        st.session_state.throughput += res_mes['EFC_Ciclos_Equivalentes'] * cap_mwh
        st.session_state.energy_charge += res_mes.get('Energia_Carga_kWh', 0)
        st.session_state.energy_discharge += res_mes.get('Energia_Descarga_kWh', 0)
        
        # Garante que a mensagem de status esteja correta no callback
        mes_atual = res_mes.get('mes', '?')
        total_p = res_mes.get('total_meses', '?')
        msg_placeholder.markdown(f'<div style="text-align: center;"><span class="pulse-icon">⚡</span><b>Simulação em Andamento: Mês {mes_atual}/{total_p}</b><br><small>(Evite interagir com menus durante o processamento para não interromper)</small></div>', unsafe_allow_html=True)

        # Renderize diretamente durante a simulação
        with metrics_placeholder.container():
            render_metrics_row(st.session_state.sim_results, st.session_state.throughput, month_idx=selected_month_idx)
        
        with charts_placeholder.container():
            # Título da Visão Atual
            title = "📊 Resumo Geral" if selected_month_idx is None else f"📅 Dados do Mês {selected_month_idx + 1}"
            st.markdown(f"### {title}")

            # Durante a simulação (live), precisamos de chaves que mudem a cada mês 
            # para não colidir com o mês anterior na mesma execução.
            n_res = len(st.session_state.sim_results)
            step_suffix = f"live_{n_res}"

            is_current = (selected_month_idx is None or selected_month_idx == n_res - 1)
            display_soc = df_soc if is_current else pd.DataFrame()
            display_in = df_in if is_current else pd.DataFrame()
            
            if view_set_live == "📊 Visão Geral":
                render_view_overview(st.session_state.sim_results, display_soc, month_idx=selected_month_idx, key_suffix=step_suffix)
            elif view_set_live == "📉 Degradação":
                render_view_degradation(st.session_state.sim_results, month_idx=selected_month_idx, key_suffix=step_suffix)
            elif view_set_live == "⚡ Operacional":
                render_view_operational(st.session_state.sim_results, display_soc, display_in, month_idx=selected_month_idx, key_suffix=step_suffix)

    async_start = st.sidebar.button("▶️ Iniciar Simulação", disabled=(st.session_state.sim_status == "running"))
    
    if async_start:
        st.session_state.sim_results = pd.DataFrame()
        st.session_state.throughput = 0.0
        st.session_state.energy_charge = 0.0
        st.session_state.energy_discharge = 0.0
        st.session_state.sim_status = "running"
        
        # Limpa e atualiza o placeholder imediatamente para remover o "Concluído" anterior
        msg_placeholder.markdown('<div style="text-align: center;"><span class="pulse-icon">⚡</span><b>Preparando Nova Simulação...</b></div>', unsafe_allow_html=True)

        cfg = CONFIGURACAO.model_copy(deep=True)
        
        # Aplica Overrides da Aba de Configurações
        cfg.modelo_degradacao = ModeloDegradacaoConfig(**st.session_state.config_override)

        cfg.bateria = PERFIS_BATERIA[battery_prof].model_copy(deep=True)
        cfg.bateria.Tbat_kelvin = t_cyc + 273.15
        cfg.bateria.Tbat_kelvin_idle = t_idl + 273.15
        cfg.bateria.soc_min = soc_min_val / 100.0
        cfg.bateria.soc_max = soc_max_val / 100.0
        cfg.simulacao.ANOS_SIMULACAO = anos_sim
        cfg.simulacao.MESES_SIMULACAO = meses_total_sim
        
        with st.spinner("Motor de Simulação em Execução..."):
            sim = SimulationManager(
                cfg, backend=backend, data_file=data_file_sidebar,
                on_mes_complete=live_callback, sim_until_eol=sim_eol_mode
            )
            sim.run()
        
        st.session_state.sim_status = "finished"
        st.rerun()

    # Render Persistent State (Quando não está rodando)
    if not st.session_state.sim_results.empty and st.session_state.sim_status != "running":
        with metrics_placeholder.container():
            render_metrics_row(st.session_state.sim_results, st.session_state.throughput, month_idx=selected_month_idx)
        with charts_placeholder.container():
            # Título da Visão Atual
            title = "📊 Resumo Geral" if selected_month_idx is None else f"📅 Dados do Mês {selected_month_idx + 1}"
            st.markdown(f"### {title}")

            is_latest = (selected_month_idx is not None and selected_month_idx == len(st.session_state.sim_results) - 1)
            display_soc = st.session_state.curr_soc if is_latest else pd.DataFrame()
            display_input = st.session_state.curr_input if is_latest else pd.DataFrame()
            
            if view_set_live == "📊 Visão Geral":
                render_view_overview(st.session_state.sim_results, display_soc, month_idx=selected_month_idx, key_suffix="live_st")
            elif view_set_live == "📉 Degradação":
                render_view_degradation(st.session_state.sim_results, month_idx=selected_month_idx, key_suffix="live_st")
            elif view_set_live == "⚡ Operacional":
                render_view_operational(st.session_state.sim_results, display_soc, display_input, month_idx=selected_month_idx, key_suffix="live_st")

# --- TAB 2: HISTORY ---
with tab_hist:
    res_path = "Results"
    if not os.path.exists(res_path):
        st.warning("Pasta 'Results' não encontrada.")
    else:
        past_sims = sorted([d for d in os.listdir(res_path) if os.path.isdir(os.path.join(res_path, d))], reverse=True)
        selected_sim = st.selectbox("Selecionar Simulação Passada", past_sims, format_func=format_sim_name)
        
        if selected_sim:
            sim_dir = os.path.join(res_path, selected_sim)
            report_file = os.path.join(sim_dir, "report.txt")




            if os.path.exists(report_file):
                with st.expander("📄 Ver Resumo do Relatório", expanded=False):
                    with open(report_file, 'r', encoding='utf-8') as f:
                        st.text(f.read())
            
            import glob
            excel_files = glob.glob(os.path.join(sim_dir, "data", "resultados_completos*.xlsx"))
            if excel_files:
                excel_file = excel_files[0]
                df_hist = pd.read_excel(excel_file)
                
                # History Selectbox
                opcoes_hist = ["📊 Resumo Geral"] + [f"📅 Mês {i+1}" for i in range(len(df_hist))]
                sel_mode_h = st.selectbox("Selecione o Foco do Histórico", opcoes_hist, index=0, key="hist_sel")
                selected_month_h = None if sel_mode_h == "📊 Resumo Geral" else int(sel_mode_h.split(" ")[-1]) - 1

                view_set_hist = st.radio("Conjunto de Visualização (Histórico)", 
                                       ["📊 Visão Geral", "📉 Degradação", "⚡ Operacional"], 
                                       horizontal=True, key="hist_view")
                
                h_cap_mwh = df_hist.get("capacidade_nominal_wh", [CONFIGURACAO.bateria.capacidade_nominal_wh])[0] / 1e6
                h_throughput = df_hist['EFC_Ciclos_Equivalentes'].sum() * h_cap_mwh
                
                render_metrics_row(df_hist, h_throughput, month_idx=selected_month_h)
                st.markdown("---")
                
                # Título da Visão Histórica Atual
                title_h = "📊 Resumo Geral (Histórico)" if selected_month_h is None else f"📅 Dados do Mês {selected_month_h + 1} (Histórico)"
                st.markdown(f"### {title_h}")

                if view_set_hist == "📊 Visão Geral":
                    render_view_overview(df_hist, pd.DataFrame(), month_idx=selected_month_h, key_suffix="hist")
                elif view_set_hist == "📉 Degradação":
                    render_view_degradation(df_hist, month_idx=selected_month_h, key_suffix="hist")
                elif view_set_hist == "⚡ Operacional":
                    render_view_operational(df_hist, pd.DataFrame(), pd.DataFrame(), month_idx=selected_month_h, key_suffix="hist")
            else:
                st.error("Arquivo de resultados não encontrado nesta pasta.")

# --- TAB 3: COMPARISON ---
with tab_comp:
    st.header("📈 Comparativo de Simulações")
    res_path = "Results"
    if os.path.exists(res_path):
        past_sims = sorted([d for d in os.listdir(res_path) if os.path.isdir(os.path.join(res_path, d))], reverse=True)
        selected_sims = st.multiselect("Selecione Simulações para Comparar", past_sims, format_func=format_sim_name)
        
        if selected_sims:
            comparison_data = []
            for sim_id in selected_sims:
                import glob
                excel_files = glob.glob(os.path.join(res_path, sim_id, "data", "resultados_completos*.xlsx"))
                if excel_files:
                    excel_file = excel_files[0]
                    df_c = pd.read_excel(excel_file)
                    df_c['Simulacao'] = sim_id
                    comparison_data.append(df_c)
            
            if comparison_data:
                df_all = pd.concat(comparison_data)
                
                # SOH Evolution Comparison
                st.subheader("Evolução do SOH (%)")
                fig_soh = px.line(df_all, x='mes', y='capacidade_restante', color='Simulacao', markers=True)
                fig_soh.update_layout(
                    height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]),
                    yaxis_range=[75, 102]
                )
                st.plotly_chart(fig_soh, use_container_width=True)
                
                # Final Degradation Comparison
                st.subheader("Dano Total Acumulado")
                final_results = df_all.groupby('Simulacao').last().reset_index()
                fig_deg = go.Figure()
                fig_deg.add_trace(go.Bar(x=final_results['Simulacao'], y=final_results['dano_ciclo_acum'], name='Dano Ciclo', marker_color=THEME_COLORS["CYCLE"]))
                fig_deg.add_trace(go.Bar(x=final_results['Simulacao'], y=final_results['dano_cal_acum'], name='Dano Cal', marker_color=THEME_COLORS["CALENDAR"]))
                fig_deg.update_layout(
                    barmode='stack', height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
                )
                st.plotly_chart(fig_deg, use_container_width=True)

                # --- Parameter Diff Table ---
                st.subheader("🕵️ Diferenças de Parâmetros")
                PARAM_LABELS = {
                    "bateria_nome": "Modelo de Bateria",
                    "bateria_cap_wh": "Capacidade Nominal (Wh)",
                    "bateria_soc_min": "SOC Mín",
                    "bateria_soc_max": "SOC Máx",
                    "backend": "Backend",
                    "data_file": "Curva de Carga",
                    "timestamp": "Data/Hora",
                    "sim_until_eol": "Modo EOL",
                    "total_meses_simulados": "Meses Simulados",
                }
                SNAP_DEG_LABELS = {
                    "a": "Ciclo: coef. a",
                    "b": "Ciclo: coef. b",
                    "c": "Ciclo: coef. c",
                    "d": "Ciclo: coef. d",
                    "k_T": "Cal: k_T",
                    "k_soc": "Cal: k_soc",
                    "exp_cal": "Cal: exp_cal",
                }

                snapshots = {}
                for sim_id in selected_sims:
                    import glob
                    snap_files = glob.glob(os.path.join(res_path, sim_id, "data", "config_snapshot*.json"))
                    if snap_files:
                        snap_file = snap_files[0]
                        with open(snap_file, "r", encoding="utf-8") as f:
                            snapshots[sim_id] = json.load(f)

                if snapshots:
                    # Preparar os dados avançados primeiro
                    dados_ia = []
                    for sim_id in selected_sims:
                        sim_data_df = df_all[df_all['Simulacao'] == sim_id]
                        last_row = sim_data_df.iloc[-1].to_dict()
                        
                        # Extrai config para os cálculos
                        sim_config = snapshots.get(sim_id, {})
                        cap_nominal_wh = sim_config.get("bateria", {}).get("capacidade_nominal_wh", 1000000)
                        dias_por_ano_avg = sim_config.get("dados_entrada", {}).get("dias_por_ano_avg", 360)
                        mod_cfg_dict = sim_config.get("modelo_degradacao", CONFIGURACAO.modelo_degradacao.model_dump())
                        
                        # 1. Calculation RUL
                        months_simulated = last_row.get('mes', 1)
                        total_damage = last_row.get('dano_ciclo_acum', 0) + last_row.get('dano_cal_acum', 0)
                        rul_anos = calcular_rul(
                            soh_atual_perc=last_row.get('capacidade_restante', 100),
                            dano_total_acumulado=total_damage,
                            meses_simulados=months_simulated,
                            dias_por_ano_avg=dias_por_ano_avg
                        )
                        
                        # 2. Calculation Severity (Global average)
                        avg_monthly_damage = total_damage / months_simulated if months_simulated > 0 else 0
                        is_val = calcular_fator_severidade(avg_monthly_damage, ModeloDegradacaoConfig(**mod_cfg_dict))
                        
                        # 3. Calculation Throughput
                        cap_mwh = cap_nominal_wh / 1e6
                        total_throughput_mwh = sim_data_df['EFC_Ciclos_Equivalentes'].sum() * cap_mwh
                        
                        total_ciclos = int(sim_data_df.get('Ciclos_Contagem', pd.Series(dtype=int)).sum())
                        last_row['Ciclos_Totais'] = total_ciclos
                        last_row['EFC_Total'] = sim_data_df['EFC_Ciclos_Equivalentes'].sum()
                        
                        # 4. Rainflow Summary
                        deep_cycles = 0
                        shallow_cycles = 0
                        for _, row in sim_data_df.iterrows():
                            raw_rf = row.get('Rainflow_Cycles', [])
                            if isinstance(raw_rf, str):
                                try: raw_rf = ast.literal_eval(raw_rf)
                                except: raw_rf = []
                            if isinstance(raw_rf, list):
                                for cycle in raw_rf:
                                    # format: [DOD, Mean, Count, Start, End]
                                    dod = cycle[0]
                                    count = cycle[2]
                                    if dod > 80:
                                        deep_cycles += count
                                    elif dod < 20:
                                        shallow_cycles += count
                                        
                        # Limpa dados desnecessários ou muito pesados
                        for k in ['Rainflow_Cycles', 'Potencia_Aplicada_kW', 'SOC_Max_Diario', 'SOC_Min_Diario', 'SOC_Medio_Diario']:
                            last_row.pop(k, None)
                        
                        dados_ia.append({
                            "Simulacao": sim_id,
                            "Parametros": sim_config,
                            "Resultados_Finais": last_row,
                            "Metricas_Avancadas": {
                                "Vida_Util_Restante_Anos": round(rul_anos, 2),
                                "Fator_Severidade_Is": round(is_val, 3),
                                "Throughput_Acumulado_MWh": round(total_throughput_mwh, 2),
                                "Resumo_Espectro_Uso": {
                                    "Ciclos_Profundos_Acima_80_DOD": deep_cycles,
                                    "Micro_Ciclos_Abaixo_20_DOD": shallow_cycles
                                }
                            }
                        })
                    
                    rows = []
                    # Parâmetros de top-level
                    for key, label in PARAM_LABELS.items():
                        vals = {s: str(v.get(key, "N/A")) for s, v in snapshots.items()}
                        unique = len(set(vals.values())) > 1
                        rows.append({"Parâmetro": label, **vals, "_diff": unique})
                        
                    # Parâmetros de degradação
                    for key, label in SNAP_DEG_LABELS.items():
                        vals = {}
                        for s, v in snapshots.items():
                            ciclo = v.get("modelo_degradacao", {}).get("ciclo", {})
                            cal = v.get("modelo_degradacao", {}).get("calendario", {})
                            vals[s] = str(ciclo.get(key, cal.get(key, "N/A")))
                        unique = len(set(vals.values())) > 1
                        rows.append({"Parâmetro": label, **vals, "_diff": unique})

                    # Métricas Finais Básicas
                    BASE_METRICS_LABELS = {
                        "capacidade_restante": "SOH Final (%)",
                        "dano_ciclo_acum": "Dano Cíclico Acumulado",
                        "dano_cal_acum": "Dano Calendário Acumulado",
                        "DOD_Medio_Perc": "DOD Médio (%)",
                        "SOC_Medio": "SOC Médio (%)",
                        "SOC_Medio_Idle": "SOC Médio em Repouso (%)",
                        "Ciclos_Totais": "Ciclos Concluídos (Total)",
                        "EFC_Total": "EFC Acumulado"
                    }
                    for key, label in BASE_METRICS_LABELS.items():
                        vals = {}
                        for dia in dados_ia:
                            met = dia.get("Resultados_Finais", {})
                            val = met.get(key, "N/A")
                            if isinstance(val, (int, float)):
                                if pd.isna(val):
                                    vals[dia["Simulacao"]] = "N/A"
                                elif key in ["dano_ciclo_acum", "dano_cal_acum"]:
                                    vals[dia["Simulacao"]] = f"{val:.4e}"
                                elif key in ["DOD_Medio_Perc", "SOC_Medio", "SOC_Medio_Idle"]:
                                    # Convert fraction to % for display
                                    vals[dia["Simulacao"]] = f"{val * 100.0:.2f}"
                                else:
                                    vals[dia["Simulacao"]] = f"{val:.2f}"
                            else:
                                vals[dia["Simulacao"]] = str(val)
                                
                        unique = len(set(vals.values())) > 1
                        rows.append({"Parâmetro": label, **vals, "_diff": unique})

                    # Métricas Avançadas
                    ADV_LABELS = {
                        "Vida_Util_Restante_Anos": "RUL Estimado (Anos)",
                        "Fator_Severidade_Is": "Severidade (Is)",
                        "Throughput_Acumulado_MWh": "Throughput Acumulado (MWh)",
                        "Ciclos_Profundos_Acima_80_DOD": "Ciclos Profundos (>80% DOD)",
                        "Micro_Ciclos_Abaixo_20_DOD": "Micro-ciclos (<20% DOD)"
                    }
                    
                    for key, label in ADV_LABELS.items():
                        vals = {}
                        for dia in dados_ia:
                            met = dia["Metricas_Avancadas"]
                            if key in met:
                                vals[dia["Simulacao"]] = str(met[key])
                            else:
                                vals[dia["Simulacao"]] = str(met["Resumo_Espectro_Uso"].get(key, "N/A"))
                        unique = len(set(vals.values())) > 1
                        rows.append({"Parâmetro": label, **vals, "_diff": unique})

                    df_diff = pd.DataFrame(rows)
                    diff_mask = df_diff.pop("_diff")

                    def highlight_diff(row):
                        idx = df_diff.index[df_diff["Parâmetro"] == row["Parâmetro"]][0]
                        color = "background-color: #2a1f00; color: #ffcc00;" if diff_mask.iloc[idx] else ""
                        return [color] * len(row)

                    st.dataframe(df_diff.style.apply(highlight_diff, axis=1), use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("🧠 Análise Inteligente (IA)")
                    st.write("Clique no botão abaixo para gerar um relatório comparativo detalhado das simulações usando a Inteligência Artificial.")
                    
                    if st.button("🚀 Gerar Análise Inteligente", key="btn_gemini_analysis", type="primary"):
                        with st.spinner("Analisando dados das simulações... Isso pode levar alguns segundos."):
                            relatorio_ia = analisar_comparacao_bess(dados_ia)
                            st.markdown("### Relatório do Especialista (Gemini)")
                            st.info("Abaixo está a análise técnica gerada pela inteligência artificial com base nas métricas comparadas.")
                            st.markdown(relatorio_ia)

                else:
                    st.info("Execute novas simulações para obter metadados comparáveis (`config_snapshot.json`).")
            else:
                st.info("Nenhuma das pastas selecionadas contém o arquivo de resultados.")
    else:
        st.warning("Pasta 'Results' não encontrada.")

# --- TAB 4: ENGINE VALIDATION ---
with tab_val:
    st.header("✔️ Validação do Motor de Simulação")
    st.write("Esta aba executa os testes de fidelidade do código-fonte contra a matemática teórica de baterias (Stroe e Rainflow).")
    
    col_gerar, col_validar = st.columns(2)
    
    with col_gerar:
        if st.button("1. Gerar Perfis Sintéticos"):
            with st.spinner(f"Gerando dados sintéticos para o perfil {battery_prof}..."):
                refresh_modules()
                st.session_state.validation_profiles = mission_profile_generator.generate_profiles(bateria_alvo=battery_prof)
            st.success(f"Perfis gerados com sucesso na pasta `data/mock_profiles/`")
            
        if st.session_state.validation_profiles:
            st.info(f"{len(st.session_state.validation_profiles)} perfis de bateria registrados.")
            
    with col_validar:
        # Pega a bateria da sidebar para validar
        if st.button("2. Executar Pipeline de Validação"):
            if not st.session_state.validation_profiles:
                st.error("Gere os perfis primeiro!")
            else:
                try:
                    with st.spinner(f"Rodando simulação paramétrica para {battery_prof} usando backend {backend}..."):
                        refresh_modules()
                        st.session_state.validation_run = test_engine_validation.rodar_validacao(perfil_nome=battery_prof, backend=backend)
                    st.success("Validação Completa!")
                except Exception as e:
                    st.error(f"Erro Crítico na Validação: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                st.info("💡 **Dica:** Se o TC1 falhar inesperadamente, certifique-se de ter clicado em '1. Gerar Perfis Sintéticos' (Botão ao lado) após qualquer alteração no código.")

    if st.session_state.validation_run:
        res = st.session_state.validation_run
        if res["status"] == "error":
            st.error("Erros na execução: " + ", ".join(res["errors"]))
        else:
            assertions = res["assertions"]
            
            # Helper para status cards individuais
            def show_test_result(title, name_key):
                ast = assertions.get(name_key, {"pass": False, "msg": "Teste não executado"})
                if ast["pass"]:
                    st.success(f"**{title}**: PASS — {ast['msg']}")
                else:
                    st.error(f"**{title}**: FAIL — {ast['msg']}")

            # --- Processamento de Métricas para Visualização ---
            try:
                from besx.domain.models.battery_simulator import picos_e_vales
                import rainflow
                
                # 1. TC1
                df_tc1 = res.get("tc1_data")
                if df_tc1 is not None and not df_tc1.empty:
                    soc_max_tc1 = df_tc1['SOC'].max() * 100.0
                    soc_min_tc1 = df_tc1['SOC'].iloc[-1] * 100.0
                else:
                    soc_max_tc1, soc_min_tc1 = 0.0, 0.0
                
                # 2. TC2
                df_tc2 = res.get("tc2_data")
                if df_tc2 is not None and not df_tc2.empty:
                    prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
                    soc_series = pd.Series(df_tc2['SOC'].values)
                    lista_simplificada = picos_e_vales(soc_series, prominence=prominence)
                    ciclos = list(rainflow.extract_cycles(lista_simplificada))
                    ciclos = [c for c in ciclos if c[0] > 0.1]
                    total_ciclos = int(sum(c[2] for c in ciclos))
                    dod_medio = (sum(c[0] * c[2] for c in ciclos)/total_ciclos if total_ciclos > 0 else 0.0) * 100.0
                else:
                    total_ciclos, dod_medio = 0, 0.0

                # 3. TC3
                hist_cd = res.get("historico_degradacao", [])
                soh_final = 100.0 - (hist_cd[-1] if hist_cd else 0.0)
            except Exception as e:
                st.error(f"Erro ao processar métricas de validação: {e}")
                df_tc1, df_tc2, hist_cd = None, None, []
                soc_max_tc1, soc_min_tc1, total_ciclos, dod_medio, soh_final = 0, 0, 0, 0, 100

            # --- TC1 Section ---
            with st.expander(f"🔍 1. TC1: 1C Ideal Swing (0-100%) - {'🟢 PASS' if assertions.get('tc1_1c_swing', {}).get('pass') else '🔴 FAIL'}", expanded=True):
                col_info, col_graph = st.columns([3, 4])
                with col_info:
                    st.markdown("""
                    **Objetivo:** Validar o integrador de Coulomb puro (fim de escala).
                    
                    **Expectativa:** O SOC deve ir de 0% a 100% e retornar a 0% cravado.
                    """)
                    
                    ast_tc1 = assertions.get("tc1_1c_swing", {"pass": False, "msg": "Teste não executado"})
                    if ast_tc1["pass"]:
                        st.success(ast_tc1["msg"])
                    else:
                        st.error(ast_tc1["msg"])
                    
                    st.markdown(f"""
                    - **SOC Máximo Atingido:** {soc_max_tc1:.2f}%
                    - **SOC Final:** {soc_min_tc1:.2f}%
                    """)
                
                with col_graph:
                    if df_tc1 is not None and not df_tc1.empty:
                        fig1 = px.line(df_tc1, x=df_tc1['Tempo']/60.0, y=df_tc1['SOC']*100.0, color_discrete_sequence=[THEME_COLORS["PRIMARY"]])
                        fig1.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), yaxis_range=[-5, 105], yaxis_title="SOC (%)", xaxis_title="Tempo (min)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
                        st.plotly_chart(fig1, use_container_width=True, key="fig_tc1_val")
            
            # --- TC2 Section ---
            with st.expander(f"📊 2. TC2: Rainflow Micro-cycles & DOD - {'🟢 PASS' if assertions.get('rainflow_dod', {}).get('pass') else '🔴 FAIL'}", expanded=False):
                col_info, col_graph = st.columns([3, 4])
                with col_info:
                    st.markdown("""
                    **Objetivo:** Validar o extrator de ciclos Rainflow e a precisão do DOD parcial.
                    
                    **Expectativa:** Detectar exatamente os ciclos com profundidade de 20%.
                    """)
                    
                    ast_tc2 = assertions.get("rainflow_dod", {"pass": False, "msg": "Teste não executado"})
                    if ast_tc2["pass"]:
                        st.success(ast_tc2["msg"])
                    else:
                        st.error(ast_tc2["msg"])
                        
                    st.markdown(f"""
                    - **Total de Ciclos Extraídos:** {total_ciclos}
                    - **DOD Médio (%):** {dod_medio:.2f}%
                    - **SOC Médio (%):** 50.0%
                    """)
                
                with col_graph:
                    if df_tc2 is not None and not df_tc2.empty:
                        df_tc2_plot = df_tc2.copy()
                        df_tc2_plot['SOC'] *= 100.0
                        fig2 = px.line(df_tc2_plot, x=df_tc2_plot['Tempo']/60.0, y='SOC', color_discrete_sequence=[THEME_COLORS["WARNING"]])
                        fig2.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), yaxis_range=[0, 105], yaxis_title="SOC (%)", xaxis_title="Tempo (min)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
                        st.plotly_chart(fig2, use_container_width=True, key="fig_tc2_val")

            # --- TC3 Section ---
            with st.expander(f"📈 3. Degradação Não-Linear (Stroe) - {'🟢 PASS' if assertions.get('stroe_nonlinear', {}).get('pass') else '🔴 FAIL'}", expanded=False):
                col_info, col_graph = st.columns([3, 4])
                with col_info:
                    st.markdown("""
                    **Objetivo:** Validar a regra de acumulação quadrática de dano cíclico.
                    
                    **Expectativa:** Dano total aos 12 meses deve ser $\sqrt{12} \\approx 3.46$ vezes o dano do primeiro mês.
                    """)
                    
                    ast_tc3 = assertions.get("stroe_nonlinear", {"pass": False, "msg": "Teste não executado"})
                    if ast_tc3["pass"]:
                        st.success(ast_tc3["msg"])
                    else:
                        st.error(ast_tc3["msg"])
                        
                    st.markdown(f"""
                    - **SOH Inicial (%):** 100.00%
                    - **SOH Final (%):** {soh_final:.2f}%
                    - **Dano Cíclico Acumulado:** {hist_cd[-1]:.6f}
                    """)
                
                with col_graph:
                    if hist_cd:
                        fig3 = px.line(x=res["history_meses"], y=hist_cd, markers=True, color_discrete_sequence=[THEME_COLORS["CALENDAR"]])
                        fig3.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), xaxis_title="Meses", yaxis_title="Dano Acumulado (%)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
                        st.plotly_chart(fig3, use_container_width=True, key="fig_tc3_val")

            st.markdown("---")
                    
# --- TAB 5: CONFIGURATION ---
with tab_cfg:
    st.header("⚙️ Ajustes do Modelo de Degradação")
    st.info("Estes valores são aplicados apenas nesta sessão. Altere com cuidado.")
    
    with st.form("degr_config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔄 Dano Cíclico")
            a_val = st.number_input("Coeficiente a", value=st.session_state.config_override["ciclo"]["a"], format="%.6f")
            b_val = st.number_input("Coeficiente b", value=st.session_state.config_override["ciclo"]["b"], format="%.6f")
            c_val = st.number_input("Coeficiente c", value=st.session_state.config_override["ciclo"]["c"], format="%.6f")
            d_val = st.number_input("Coeficiente d", value=st.session_state.config_override["ciclo"]["d"], format="%.6f")
        
        with col2:
            st.subheader("⏳ Dano Calendário")
            kt_val = st.number_input("k_T", value=st.session_state.config_override["calendario"]["k_T"], format="%.2e")
            ksoc_val = st.number_input("k_soc", value=st.session_state.config_override["calendario"]["k_soc"], format="%.6f")
            exp_cal_val = st.number_input("Expoente Cal", value=st.session_state.config_override["calendario"]["exp_cal"], format="%.2f")

        if st.form_submit_button("Aplicar Configurações"):
            st.session_state.config_override["ciclo"]["a"] = a_val
            st.session_state.config_override["ciclo"]["b"] = b_val
            st.session_state.config_override["ciclo"]["c"] = c_val
            st.session_state.config_override["ciclo"]["d"] = d_val
            st.session_state.config_override["calendario"]["k_T"] = kt_val
            st.session_state.config_override["calendario"]["k_soc"] = ksoc_val
            st.session_state.config_override["calendario"]["exp_cal"] = exp_cal_val
            st.success("Configurações aplicadas com sucesso!")
