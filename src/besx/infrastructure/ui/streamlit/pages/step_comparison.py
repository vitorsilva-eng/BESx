import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import json
import ast
# Imports adiados para evitar KeyError no startup
from besx.domain.models.degradation_model import calcular_fator_severidade, calcular_rul
from besx.config import CONFIGURACAO, ModeloDegradacaoConfig
from besx.infrastructure.llm.gemini_analyzer import analisar_comparacao_bess

def render_step_comparison():
    """
    Passo 5: Comparativo A/B de Simulações.
    """
    from besx.infrastructure.ui.streamlit.utils.render_utils import (
        format_sim_name, THEME_COLORS
    )
    st.header("📈 Passo 5: Comparativo de Simulações")
    st.markdown("Compare diferentes cenários de operação e baterias para encontrar a melhor viabilidade.")

    res_path = "results"
    if not os.path.exists(res_path) or not os.listdir(res_path):
        st.warning("Nenhuma simulação no histórico para comparar.")
        return

    past_sims = sorted([d for d in os.listdir(res_path) if os.path.isdir(os.path.join(res_path, d))], reverse=True)
    selected_sims = st.multiselect("Selecione Simulações para Comparar", past_sims, format_func=format_sim_name)
    
    if not selected_sims:
        st.info("💡 Selecione pelo menos duas simulações acima para ver a comparação.")
        return

    comparison_data = []
    snapshots = {}
    
    for sim_id in selected_sims:
        sim_dir = os.path.join(res_path, sim_id)
        sim_data_path = os.path.join(sim_dir, "data")
        pkl_files = glob.glob(os.path.join(sim_data_path, "resultados_completos*.pkl"))
        excel_files = glob.glob(os.path.join(sim_data_path, "resultados_completos*.xlsx"))
        snap_files = glob.glob(os.path.join(sim_data_path, "config_snapshot*.json"))
        
        df_c = None
        if pkl_files:
            df_c = pd.read_pickle(pkl_files[0])
        elif excel_files:
            df_c = pd.read_excel(excel_files[0])
            
        if df_c is not None:
            df_c['Simulacao'] = sim_id
            comparison_data.append(df_c)
            
        if snap_files:
            with open(snap_files[0], "r", encoding="utf-8") as f:
                snapshots[sim_id] = json.load(f)

    if len(comparison_data) < 1:
        st.error("Dados insuficientes para comparação.")
        return

    df_all = pd.concat(comparison_data)
    
    # Visual Comparisons
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Evolução do SOH (%)")
        fig_soh = px.line(df_all, x='mes', y='capacidade_restante', color='Simulacao', markers=True)
        fig_soh.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
        st.plotly_chart(fig_soh, width="stretch")

    with col2:
        st.subheader("Dano Acumulado (Final)")
        final_rows = df_all.groupby('Simulacao').last().reset_index()
        fig_deg = go.Figure()
        fig_deg.add_trace(go.Bar(x=final_rows['Simulacao'], y=final_rows['dano_ciclo_acum'], name='Dano Ciclo', marker_color=THEME_COLORS["CYCLE"]))
        fig_deg.add_trace(go.Bar(x=final_rows['Simulacao'], y=final_rows['dano_cal_acum'], name='Dano Cal', marker_color=THEME_COLORS["CALENDAR"]))
        fig_deg.update_layout(barmode='stack', height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
        st.plotly_chart(fig_deg, width="stretch")

    st.markdown("---")
    
    # Detailed Diff Table
    st.subheader("🕵️ Confronto de Parâmetros e Resultados")
    render_diff_table(df_all, selected_sims, snapshots)
    
    st.markdown("---")
    
    # IA Analysis
    st.subheader("🤖 Análise Especialista (IA)")
    if st.button("🚀 Gerar Insights com IA", type="primary"):
        with st.spinner("O Gemini está analisando os dados..."):
            # Prepare data for IA (This is a simplification of the logic found in streamlit_app)
            ia_payload = []
            for sim_id in selected_sims:
                df_sim = df_all[df_all['Simulacao'] == sim_id]
                last = df_sim.iloc[-1].to_dict()
                ia_payload.append({
                    "Simulacao": sim_id,
                    "Resultados_Finais": last,
                    "Parametros": snapshots.get(sim_id, {})
                })
            
            report = analisar_comparacao_bess(ia_payload)
            st.markdown(report)

def render_diff_table(df_all, selected_sims, snapshots):
    # Parameter Labels
    LABELS = {
        "bateria_nome": "Bateria", "bateria_cap_wh": "Capacidade (Wh)",
        "bateria_soc_min": "SOC Mín", "bateria_soc_max": "SOC Máx",
        "backend": "Motor", "total_meses_simulados": "Meses",
        "capacidade_restante": "SOH Final (%)", "EFC_Total": "EFC Acumulado"
    }
    
    rows = []
    for key, label in LABELS.items():
        row = {"Métrica/Parâmetro": label}
        vals = []
        for sim_id in selected_sims:
            # Check in snapshot first
            val = snapshots.get(sim_id, {}).get(key)
            if val is None:
                # Check in results
                df_sim = df_all[df_all['Simulacao'] == sim_id]
                if key == "EFC_Total": val = df_sim['EFC_Ciclos_Equivalentes'].sum()
                else: val = df_sim.iloc[-1].get(key, "N/A")
            
            # Formatting
            if isinstance(val, float): 
                if "SOH" in label or "SOC" in label:
                    if val <= 1.0: val *= 100.0
                    row[sim_id] = f"{val:.2f}%"
                else: row[sim_id] = f"{val:.2f}"
            else: row[sim_id] = str(val)
            vals.append(row[sim_id])
        
        row["_diff"] = len(set(vals)) > 1
        rows.append(row)
        
    df_res = pd.DataFrame(rows)
    diff_mask = df_res.pop("_diff")

    def style_diff(row):
        idx = df_res.index[df_res["Métrica/Parâmetro"] == row["Métrica/Parâmetro"]][0]
        return ["background-color: #2a1f00; color: #ffcc00;" if diff_mask.iloc[idx] else ""] * len(row)

    st.dataframe(df_res.style.apply(style_diff, axis=1), width="stretch")
