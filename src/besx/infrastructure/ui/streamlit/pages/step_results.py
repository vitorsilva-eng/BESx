import streamlit as st
import pandas as pd
import os
from besx.infrastructure.ui.streamlit.utils.render_utils import (
    render_metrics_row, render_view_overview, 
    render_view_degradation, render_view_operational,
    format_sim_name
)

def render_step_results():
    """
    Passo 4: Visualização de Resultados e Histórico.
    """
    st.header("📊 Passo 4: Resultados da Simulação")
    st.markdown("Explore o comportamento da bateria ao longo do tempo e valide o impacto financeiro/técnico.")

    res_path = "results"
    if not os.path.exists(res_path) or not os.listdir(res_path):
        # Fallback: Se não há histórico, checa se acabou de rodar uma simulação
        if st.session_state.get('sim_results') is not None and not st.session_state.sim_results.empty:
            df_active = st.session_state.sim_results
            st.info("💡 Exibindo resultados da simulação atual.")
            render_dashboard(df_active, "active")
        else:
            st.warning("Nenhuma simulação encontrada no histórico. Execute o Passo 3 primeiro.")
            return
    else:
        # Seletor de Histórico
        past_sims = sorted([d for d in os.listdir(res_path) if os.path.isdir(os.path.join(res_path, d))], reverse=True)
        
        # Adiciona a simulação ativa (se houver) ao topo da lista
        options = past_sims
        selected_sim = st.selectbox("Selecione uma Simulação para Analisar", options, format_func=format_sim_name)
        
        if selected_sim:
            sim_dir = os.path.join(res_path, selected_sim)
            sim_data_path = os.path.join(sim_dir, "data")
            import glob
            pkl_files = glob.glob(os.path.join(sim_data_path, "resultados_completos*.pkl"))
            
            if pkl_files:
                df_hist = pd.read_pickle(pkl_files[0])
                render_dashboard(df_hist, selected_sim)
            else:
                # Fallback para Excel se for simulação antiga
                excel_files = glob.glob(os.path.join(sim_data_path, "resultados_completos*.xlsx"))
                if excel_files:
                    df_hist = pd.read_excel(excel_files[0])
                    render_dashboard(df_hist, selected_sim)
                else:
                    st.error("Arquivo de dados não encontrado para esta simulação.")

def render_dashboard(df, key_id):
    """Renderiza o dashboard completo para um DataFrame de resultados."""
    # Metrics calculation (Aggregated from DataFrame)
    e_c_total = df['Energia_Carga_kWh'].sum()
    e_d_total = df['Energia_Descarga_kWh'].sum()
    throughput_total = (e_c_total + e_d_total) / 1000 # MWh
    
    # Selectbox for Focus
    n_meses = len(df)
    opcoes = ["📊 Resumo Geral"] + [f"📅 Mês {i+1}" for i in range(n_meses)]
    sel_mode = st.selectbox("Foco da Análise", opcoes, index=0, key=f"foco_{key_id}")
    month_idx = None if sel_mode == "📊 Resumo Geral" else int(sel_mode.split(" ")[-1]) - 1
    
    # View selection
    c1, c2 = st.columns([3, 1])
    with c1:
        view_set = st.radio("Conjunto de Dados", ["📊 Visão Geral", "📉 Degradação", "⚡ Operacional"], horizontal=True, key=f"view_{key_id}")
    with c2:
        # Exportação sob demanda para Excel
        if st.button("📥 Exportar Excel", width='stretch', key=f"export_{key_id}"):
            with st.spinner("Gerando..."):
                import io
                output = io.BytesIO()
                # Remove colunas complexas (telemetria amostrada) para evitar erros no Excel
                df_export = df.copy()
                if 'df_soc_amostrado' in df_export.columns:
                    df_export = df_export.drop(columns=['df_soc_amostrado'])
                if 'Rainflow_Cycles' in df_export.columns:
                    df_export = df_export.drop(columns=['Rainflow_Cycles'])
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_export.to_excel(writer, index=False)
                
                st.download_button(
                    label="✅ Clique p/ Baixar",
                    data=output.getvalue(),
                    file_name=f"resultados_besx_{key_id}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width='stretch'
                )

    st.markdown("---")
    render_metrics_row(df, throughput_total, e_c_total, e_d_total, month_idx=month_idx)
    st.markdown("---")
    
    # Charts
    if view_set == "📊 Visão Geral":
        render_view_overview(df, pd.DataFrame(), month_idx=month_idx, key_suffix=key_id)
    elif view_set == "📉 Degradação":
        render_view_degradation(df, month_idx=month_idx, key_suffix=key_id)
    elif view_set == "⚡ Operacional":
        render_view_operational(df, pd.DataFrame(), pd.DataFrame(), month_idx=month_idx, key_suffix=key_id)
