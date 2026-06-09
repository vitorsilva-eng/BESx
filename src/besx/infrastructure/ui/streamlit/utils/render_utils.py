import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import datetime
import ast
from typing import Optional
from besx.config import CONFIGURACAO, ModeloDegradacaoConfig
from besx.domain.models.degradation_model import calcular_fator_severidade, calcular_rul

# --- Theme Constants ---
THEME_COLORS = {
    "PRIMARY": "#00f2ff",
    "SECONDARY": "#7000ff",
    "SUCCESS": "#00ff88",
    "WARNING": "#ffaa00",
    "DANGER": "#ff0055",
    "TEXT": "#ffffff",
    "GRID": "rgba(255,255,255,0.1)",
    "CYCLE": "#00e5ff",
    "CALENDAR": "#ff00d4",
    "GLASS_BG": "rgba(255, 255, 255, 0.05)",
    "GLASS_BORDER": "rgba(255, 255, 255, 0.1)"
}

def get_status_color(value):
    """Retorna a cor neon baseada no valor (SOH ou similar)."""
    if value > 95: return THEME_COLORS["SUCCESS"]
    if value > 85: return THEME_COLORS["WARNING"]
    return THEME_COLORS["DANGER"]

def render_glass_battery(soh, label="SOH"):
    """Renderiza uma bateria estilo Glassmorphism (Vidro/Neon)."""
    color = get_status_color(soh)
    glow = f"{color}66" # Adiciona transparência para o glow
    
    st.markdown(f"""
    <div style="background: {THEME_COLORS['GLASS_BG']}; backdrop-filter: blur(10px); border: 1px solid {THEME_COLORS['GLASS_BORDER']}; 
                border-radius: 15px; padding: 20px; display: flex; flex-direction: column; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <div style="width: 50px; height: 90px; border: 2px solid rgba(255,255,255,0.2); border-radius: 6px; position: relative; padding: 2px; margin-bottom: 10px;">
            <div style="width: 25px; height: 6px; background: rgba(255,255,255,0.2); position: absolute; top: -8px; left: 12px; border-radius: 2px 2px 0 0;"></div>
            <div style="width: 100%; height: {max(5, soh)}%; background: linear-gradient(180deg, {color} 0%, rgba(0,0,0,0) 100%); 
                        position: absolute; bottom: 2px; left: 0; border-radius: 0 0 4px 4px; box-shadow: 0 -3px 10px {glow}; transition: height 0.5s ease;"></div>
        </div>
        <div style="color: {color}; font-size: 18px; font-weight: bold;">{soh:.1f}%</div>
        <div style="color: grey; font-size: 10px; text-transform: uppercase;">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_ev_battery(soh, label="HEALTH"):
    """Renderiza uma bateria estilo EV Dashboard (Segmentada)."""
    color = get_status_color(soh)
    num_segments = 10
    active_segments = int((soh / 100) * num_segments)
    
    segments_html = ""
    for i in range(num_segments):
        opacity = 1.0 if i < active_segments else 0.15
        glow_style = f"box-shadow: 0 0 8px {color};" if opacity == 1.0 else ""
        segments_html += f'<div style="height: 8px; width: 100%; background: {color}; margin: 3px 0; border-radius: 2px; opacity: {opacity}; {glow_style}"></div>'

    st.markdown(f"""
    <div style="background: #1a1c23; border-radius: 15px; padding: 20px; border-left: 4px solid {color}; min-width: 120px;">
        <div style="color: grey; font-size: 10px; margin-bottom: 8px; font-weight: bold;">{label}</div>
        <div style="display: flex; flex-direction: column-reverse;">
            {segments_html}
        </div>
        <div style="color: {color}; font-size: 24px; font-weight: 800; margin-top: 10px;">{soh:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

def format_sim_name(sim_id):
    """Formata o nome da simulação para exibição."""
    res_path = "results"
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
            parts = sim_id.split('_')
            if len(parts) >= 2:
                ts_str = f"{parts[-2]}_{parts[-1]}"
                try:
                    dt = datetime.datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                    dt_f = dt.strftime("%d/%m/%Y %H:%M:%S")
                except: dt_f = sim_id
            else: dt_f = sim_id
            return f"[{backend}] {bateria} | {meses} meses | {dt_f}"
        except: return sim_id
    return sim_id

def render_metrics_row(
    df_results: pd.DataFrame,
    throughput_mwh: float = 0.0,
    energy_charge: float = 0.0,
    energy_discharge: float = 0.0,
    month_idx: Optional[int] = None
) -> None:
    """Renders the KPI metrics row for the selected focus month or final summary.

    Args:
        df_results: DataFrame containing simulation results per month.
        throughput_mwh: Total accumulated throughput in MWh.
        energy_charge: Total charging energy in kWh.
        energy_discharge: Total discharging energy in kWh.
        month_idx: The 0-based index of the focus month. If None, renders final summary.
    """
    if df_results.empty:
        return
    
    if month_idx is None:
        target_data = df_results.iloc[-1]
        label_suffix = "(Final)"
        delta_soh = target_data['capacidade_restante'] - 100.0
    else:
        target_data = df_results.iloc[month_idx]
        label_suffix = f"(Mês {month_idx + 1})"
        if month_idx == 0:
            delta_soh = target_data['capacidade_restante'] - 100.0
        else:
            prev_data = df_results.iloc[month_idx - 1]
            delta_soh = target_data['capacidade_restante'] - prev_data['capacidade_restante']
    
    display_soh = target_data['capacidade_restante']
    
    cols1 = st.columns(4)
    cols2 = st.columns(4)
    
    with cols1[0]:
        render_ev_battery(display_soh, label="SOH " + label_suffix)

    cols1[1].metric(f"SOH {label_suffix}", f"{target_data['capacidade_restante']:.2f}%", f"{delta_soh:.2f}%")
    
    with cols1[2]:
        dano_mes = df_results['dano_ciclos_mes'].mean() + df_results['dano_cal_mes'].mean() if month_idx is None else (target_data.get('dano_ciclos_mes', 0) + target_data.get('dano_cal_mes', 0))
        mod_cfg = ModeloDegradacaoConfig(**st.session_state.get('config_override', CONFIGURACAO.modelo_degradacao.model_dump()))
        is_val = calcular_fator_severidade(dano_mes, mod_cfg)
        st.metric(f"Severidade (Is) {label_suffix}", f"{is_val:.3f}")

    with cols1[3]:
        n_meses = target_data['mes']
        if n_meses > 0:
            if display_soh <= 80.01:
                st.metric("RUL (Vida Restante)", "Limite (EOL)", "-20%")
            else:
                # Cálculo de RUL Não-Linear Otimizado
                d_cic_mean = df_results['dano_ciclos_mes'].mean()
                d_cal_mean = df_results['dano_cal_mes'].mean()
                acum_cic = target_data['dano_ciclo_acum']
                acum_cal = target_data['dano_cal_acum']
                exp_cal = CONFIGURACAO.modelo_degradacao.calendario.exp_cal
                
                rul_anos = calcular_rul(
                    display_soh,
                    d_cic_mean,
                    d_cal_mean,
                    acum_cic,
                    acum_cal,
                    exp_cal,
                    CONFIGURACAO.dados_entrada.dias_por_ano_avg
                )
                
                label_rul = f"{max(0, rul_anos):.1f} anos" if rul_anos < 50 else "> 50 anos"
                
                # Exibir Vida Útil Total Estimada para evitar mal-entendidos
                anos_simulados = n_meses / 12.0
                vida_total_estimada = anos_simulados + max(0.0, rul_anos)
                
                st.metric(
                    label="RUL (Vida Restante)", 
                    value=label_rul,
                    delta=f"Vida Total: {vida_total_estimada:.1f} anos",
                    delta_color="normal"
                )
        else: 
            st.metric("RUL (Vida Restante)", "---")


    cols2[0].metric("Throughput (MWh)", f"{throughput_mwh:.3f}")
    
    e_c = energy_charge if month_idx is None else target_data.get('Energia_Carga_kWh', 0)
    e_d = energy_discharge if month_idx is None else target_data.get('Energia_Descarga_kWh', 0)
    
    cols2[1].metric(f"Carga {label_suffix}", f"{e_c:.1f} kWh" if e_c < 10000 else f"{e_c/1000:.2f} MWh")
    cols2[2].metric(f"Descarga {label_suffix}", f"{e_d:.1f} kWh" if e_d < 10000 else f"{e_d/1000:.2f} MWh")
    cols2[3].metric(f"EFC {label_suffix}", f"{df_results['EFC_Ciclos_Equivalentes'].max():.1f}" if month_idx is None else f"{target_data.get('EFC_Ciclos_Equivalentes', 0):.1f}")

def render_view_overview(df_results, df_soc_mes, month_idx=None, key_suffix=""):
    c1, c2 = st.columns(2)
    with c1:
        if month_idx is not None:
            st.subheader(f"Curva de SOC - Mês {month_idx + 1}")
            if not df_soc_mes.empty:
                df_p = df_soc_mes.copy()
                if df_p['SOC'].max() <= 1.1: df_p['SOC'] *= 100.0
                fig = px.line(df_p, x=df_p['Tempo']/3600, y='SOC', color_discrete_sequence=[THEME_COLORS["PRIMARY"]])
                fig.update_layout(xaxis_title="Horas", yaxis_title="SOC (%)", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]), xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]))
                st.plotly_chart(fig, width="stretch", key=f"soc_chart_{key_suffix}")
            else: st.info("Perfil de SOC não disponível.")
        else:
            st.subheader("Evolução Mensal do SOH (%)")
            if not df_results.empty:
                fig = px.line(df_results, x='mes', y='capacidade_restante', markers=True, color_discrete_sequence=[THEME_COLORS["PRIMARY"]])
                fig.add_hline(y=80, line_dash="dash", line_color=THEME_COLORS["DANGER"], annotation_text="EOL")
                fig.update_layout(yaxis_range=[75, 105], height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]), xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]))
                st.plotly_chart(fig, width="stretch", key=f"soh_evol_{key_suffix}")
            
    with c2:
        if month_idx is not None:
            st.subheader(f"Dano Mensal - Mês {month_idx + 1}")
            t_d = df_results.iloc[month_idx]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=['Ciclo'], y=[t_d['dano_ciclos_mes']], name='Ciclo', marker_color=THEME_COLORS["CYCLE"]))
            fig.add_trace(go.Bar(x=['Calendário'], y=[t_d['dano_cal_mes']], name='Calendário', marker_color=THEME_COLORS["CALENDAR"]))
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]), xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]))
            st.plotly_chart(fig, width="stretch", key=f"damage_month_{key_suffix}")
        else:
            st.subheader("Razão de Dano Acumulado")
            if not df_results.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_results['mes'], y=df_results['dano_ciclo_acum'], name='Dano Ciclo', stackgroup='one', groupnorm='percent', line=dict(color=THEME_COLORS["CYCLE"])))
                fig.add_trace(go.Scatter(x=df_results['mes'], y=df_results['dano_cal_acum'], name='Dano Cal', stackgroup='one', groupnorm='percent', line=dict(color=THEME_COLORS["CALENDAR"])))
                fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]), xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]), xaxis_title="Meses")
                st.plotly_chart(fig, width="stretch", key=f"damage_accum_{key_suffix}")

def render_view_degradation(df_results, month_idx=None, key_suffix=""):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("DOD Médio vs Limite")
        if not df_results.empty:
            if month_idx is None:
                df_p = df_results.copy(); df_p['DOD_Medio_Perc'] *= 100.0
                fig = px.bar(df_p, x='mes', y='DOD_Medio_Perc', color_discrete_sequence=[THEME_COLORS["WARNING"]])
            else:
                t_d = df_results.iloc[month_idx]
                fig = px.bar(x=[f"Mês {month_idx+1}"], y=[t_d['DOD_Medio_Perc'] * 100.0], color_discrete_sequence=[THEME_COLORS["WARNING"]])
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]), xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]))
            st.plotly_chart(fig, width="stretch", key=f"dod_bar_{key_suffix}")
    with c2:
        st.subheader("Composição da Degradação")
        if not df_results.empty:
            last = df_results.iloc[-1] if month_idx is None else df_results.iloc[month_idx]
            v = [last['dano_ciclo_acum'], last['dano_cal_acum']] if month_idx is None else [last['dano_ciclos_mes'], last['dano_cal_mes']]
            fig = px.pie(values=v, names=['Cíclico', 'Calendário'], hole=0.4, color_discrete_sequence=[THEME_COLORS["CYCLE"], THEME_COLORS["CALENDAR"]])
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
            st.plotly_chart(fig, width="stretch", key=f"deg_pie_{key_suffix}")

    if not df_results.empty:
        all_rf = []
        if month_idx is not None:
            raw = df_results.iloc[month_idx].get('Rainflow_Cycles', [])
            if isinstance(raw, str):
                try: raw = ast.literal_eval(raw)
                except: raw = []
            all_rf.extend(raw)
        else:
            for _, row in df_results.iterrows():
                raw = row.get('Rainflow_Cycles', [])
                if isinstance(raw, str):
                    try: raw = ast.literal_eval(raw)
                    except: raw = []
                all_rf.extend(raw)
        
        if all_rf:
            st.markdown("---")
            st.subheader("📊 Espectro de Uso (DOD Rainflow)")
            df_rf = pd.DataFrame(all_rf, columns=['DOD', 'Mean', 'Count', 'Start', 'End'])
            if df_rf['DOD'].max() <= 1.1: df_rf['DOD'] *= 100.0
            
            cR1, cR2 = st.columns(2)
            with cR1:
                fig = px.histogram(df_rf, x='DOD', y='Count', nbins=20, color_discrete_sequence=[THEME_COLORS["CYCLE"]])
                fig.update_layout(title="Histograma de DOD", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
                st.plotly_chart(fig, width="stretch", key=f"rf_hist_{key_suffix}")
            with cR2:
                df_rf_p = df_rf.copy()
                if df_rf_p['Mean'].max() <= 1.1: df_rf_p['Mean'] *= 100.0
                fig = px.scatter(df_rf_p, x='Mean', y='DOD', size='Count', color='Count', color_continuous_scale='Inferno')
                fig.update_layout(title="Matriz de Fadiga", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
                st.plotly_chart(fig, width="stretch", key=f"rf_scatter_{key_suffix}")

def render_view_operational(
    df_results: pd.DataFrame,
    df_soc_mes: pd.DataFrame,
    df_input_mes: pd.DataFrame,
    month_idx: Optional[int] = None,
    key_suffix: str = ""
) -> None:
    """Renders the detailed operational time-series charts for electrical analysis.

    Args:
        df_results: DataFrame containing simulation results per month.
        df_soc_mes: Optional DataFrame containing raw SOC telemetry.
        df_input_mes: Optional DataFrame containing raw input data.
        month_idx: The 0-based index of the focus month. If None, shows warning.
        key_suffix: Unique suffix for Streamlit widgets to avoid duplicate IDs.
    """
    if month_idx is None:
        st.info("Selecione um mês para análise operacional.")
        return
    df_p = pd.DataFrame()
    if not df_soc_mes.empty:
        step = max(1, len(df_soc_mes) // 1500)
        df_p = df_soc_mes.iloc[::step].copy()
    elif not df_results.empty:
        try:
            raw = df_results.iloc[month_idx].get('df_soc_amostrado', [])
            if isinstance(raw, str): raw = ast.literal_eval(raw)
            if raw: df_p = pd.DataFrame(raw)
        except: pass

    if df_p.empty:
        st.warning("Séries temporais ausentes para este período.")
        return

    # 1. Converter o eixo X de segundos para strings datetime ISO contínuas no mês focado
    import datetime
    ano_adicional = month_idx // 12
    mes_ref = (month_idx % 12) + 1
    ano_ref = 2026 + ano_adicional
    data_base = datetime.datetime(ano_ref, mes_ref, 1, 0, 0, 0)
    
    x_datetime = [(data_base + datetime.timedelta(seconds=float(t))).strftime("%Y-%m-%d %H:%M:%S") for t in df_p['Tempo']]

    st.subheader(f"Análise Elétrica - Mês {month_idx + 1}")
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=("Tensão (V)", "Corrente (A)", "Potência (kW)", "SOC (%)"))
    if 'Tensao_Term_V' in df_p.columns: fig.add_trace(go.Scatter(x=x_datetime, y=df_p['Tensao_Term_V'], name="Tensão", line_color=THEME_COLORS["SECONDARY"]), row=1, col=1)
    if 'Corrente_A' in df_p.columns: fig.add_trace(go.Scatter(x=x_datetime, y=df_p['Corrente_A'], name="Corrente", line_color=THEME_COLORS["CYCLE"]), row=2, col=1)
    if 'Potencia_CA_kW' in df_p.columns: fig.add_trace(go.Scatter(x=x_datetime, y=df_p['Potencia_CA_kW'], name="Potência", fill='tozeroy', line_color=THEME_COLORS["CALENDAR"]), row=3, col=1)
    soc = df_p['SOC'] * 100.0 if df_p['SOC'].max() <= 1.1 else df_p['SOC']
    fig.add_trace(go.Scatter(x=x_datetime, y=soc, name="SOC", line_color=THEME_COLORS["PRIMARY"]), row=4, col=1)
    fig.update_layout(height=700, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]), showlegend=False)
    fig.update_xaxes(type="date", gridcolor=THEME_COLORS["GRID"])
    st.plotly_chart(fig, width="stretch", key=f"timeseries_{key_suffix}")

    # Novo Gráfico Comparativo de Despacho e Intervenção de Carga
    has_carga = 'Carga_W' in df_p.columns
    has_ems = 'Potencia_W' in df_p.columns
    has_sim = 'Potencia_CA_kW' in df_p.columns
    
    st.markdown("---")
    st.subheader(f"Comparativo de Despacho e Intervenção - Mês {month_idx + 1}")
    
    if not (has_carga and has_ems):
        st.info("💡 **Dica:** Para visualizar a comparação completa contendo a Potência Original do Cliente, a Potência com a Bateria e a Potência Disponível (EMS), lembre-se de re-executar o Passo 1 (Gerar Preview e Injetar) e o Passo 3 (Simular) com a nova versão do motor.")
    
    st.markdown(
        "Este gráfico compara a demanda original do cliente com o comportamento do sistema após a intervenção "
        "do BESS, exibindo o setpoint desejado do EMS, a potência real simulada e o respectivo SOC da bateria."
    )
    
    from plotly.subplots import make_subplots
    fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Destaque do Horário de Ponta (18h-21h nos dias úteis)
    dias_unicos = sorted(list(set([dt.split(" ")[0] for dt in x_datetime])))
    shapes = []
    for dia_str in dias_unicos:
        partes = [int(p) for p in dia_str.split("-")]
        dia_obj = datetime.date(partes[0], partes[1], partes[2])
        if dia_obj.weekday() < 5: # Segunda a Sexta
            t_start = f"{dia_str} 18:00:00"
            t_end = f"{dia_str} 21:00:00"
            
            shapes.append(dict(
                type="rect",
                xref="x",
                yref="paper",
                x0=t_start,
                x1=t_end,
                y0=0,
                y1=1,
                fillcolor="rgba(255, 0, 85, 0.08)", # Rosa/Magenta Neon translúcido para destaque sutil
                line_width=0,
                layer="below"
            ))
            
    # Trace fictício apenas para exibir o Destaque do Horário de Ponta na legenda
    fig_comp.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(color="rgba(255, 0, 85, 0.25)", symbol="square", size=10),
        name="Horário de Ponta (18h-21h)",
        showlegend=True
    ), secondary_y=False)
    
    # 1. Potência Original do Cliente
    if has_carga:
        fig_comp.add_trace(go.Scatter(
            x=x_datetime, y=df_p['Carga_W'] / 1000.0,
            name="Potência original do cliente",
            line=dict(color='#5072FF', width=2),
            opacity=0.6
        ), secondary_y=False)
        
    # 2. Potência com a Bateria (Demanda líquida vista pela rede)
    if has_carga and has_sim:
        pot_com_bateria = (df_p['Carga_W'] / 1000.0) + df_p['Potencia_CA_kW']
        fig_comp.add_trace(go.Scatter(
            x=x_datetime, y=pot_com_bateria,
            name="Potência com a Bateria",
            line=dict(color='#00ffcc', width=2.5)
        ), secondary_y=False)
        
    # 3. Potência Disponível para a bateria (Setpoint EMS desejado)
    if has_ems:
        fig_comp.add_trace(go.Scatter(
            x=x_datetime, y=df_p['Potencia_W'] / 1000.0,
            name="Potência Disponível para a bateria",
            line=dict(color='#ffaa00', width=1.5, dash='dash')
        ), secondary_y=False)
        
    # 4. Potência da Bateria (Potência CA Simulada real)
    if has_sim:
        fig_comp.add_trace(go.Scatter(
            x=x_datetime, y=df_p['Potencia_CA_kW'],
            name="Potência da Bateria",
            fill='tozeroy',
            line=dict(color='#ff0055', width=1.8)
        ), secondary_y=False)
        
    # 5. SOC da Bateria (Eixo Y Secundário à Direita)
    if has_sim:
        soc_values = df_p['SOC'] * 100.0 if df_p['SOC'].max() <= 1.1 else df_p['SOC']
        fig_comp.add_trace(go.Scatter(
            x=x_datetime, y=soc_values,
            name="SOC Bateria (%)",
            line=dict(color='#00f2ff', width=2),
            opacity=0.85
        ), secondary_y=True)
        
    fig_comp.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=THEME_COLORS["TEXT"]),
        xaxis=dict(gridcolor=THEME_COLORS["GRID"], title="Dia e Horário", type="date"),
        yaxis=dict(gridcolor=THEME_COLORS["GRID"], title="Potência (kW)"),
        yaxis2=dict(
            title="SOC (%)", 
            overlaying='y', 
            side='right', 
            range=[0, 105],
            gridcolor='rgba(0,0,0,0)' # Remove linhas de grade secundárias para manter o gráfico limpo
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5
        ),
        shapes=shapes,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    st.plotly_chart(fig_comp, width="stretch", key=f"dispatch_comp_{key_suffix}")
