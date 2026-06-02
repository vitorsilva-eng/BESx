import streamlit as st
from besx.infrastructure.logging.logger import logger
from besx.config import CONFIGURACAO
import os
import io

def render_step_rules():
    """
    Passo 1: Definição das Regras do Local e Estratégia EMS.
    """
    import pandas as pd
    import numpy as np
    import holidays
    from besx.application.ems.ems_manager import EMSManager, LoadShiftingStrategy, PeakShavingStrategy, PowerFactorCorrectionStrategy, CombinedStrategyLSPS
    from besx.application.analysis.load_analyzer import LoadAnalyzer
    from besx.infrastructure.visualization.plotly_plots import (
        plot_ems_dispatch_comparison, 
        plot_energy_balance,
        plot_load_frequency_histogram,
        plot_load_heatmap,
        plot_peak_analysis,
        plot_reactive_power_comparison,
        plot_power_factor_comparison
    )

    st.header("📋 Passo 1: Regras do Local e Estratégia EMS")
    st.markdown("Nesta etapa, definimos o perfil de consumo do cliente e as regras da concessionária.")

    # --- FUNÇÃO DE CALLBACK PARA INJEÇÃO ---
    def save_ems_profile():
        if st.session_state.get('ems_preview_result') is not None:
            from besx.config import PATH_DATABASE
            os.makedirs(PATH_DATABASE, exist_ok=True)
            
            df_res = st.session_state.ems_preview_result
            client_slug = st.session_state.get('ems_cliente', 'CLIENTE').replace(" ", "_").strip() or "CLIENTE"
            proj_slug = st.session_state.get('ems_projeto', 'PROJETO').replace(" ", "_").strip() or "PROJETO"
            filename = f"ems_{client_slug}_{proj_slug}.csv"
            save_path = os.path.join(PATH_DATABASE, filename)
            
            # Calculo do tempo em minutos relativo ao primeiro registro
            time_col = st.session_state.get('ems_time_col') or df_res.columns[0]
            df_res[time_col] = pd.to_datetime(df_res[time_col]) # Defensive
            t_delta_min = (df_res[time_col] - df_res[time_col].iloc[0]).dt.total_seconds() / 60.0
            
            df_sim = pd.DataFrame({
                'Tempo': t_delta_min,
                'Potencia_W': df_res['Potencia_Bateria_W']
            })
            
            try:
                # Salva o Pickle (.pkl) para carga instantânea no Passo 3 do BESx
                save_path_pkl = save_path.replace('.csv', '.pkl')
                df_sim.to_pickle(save_path_pkl)
                
                st.session_state.ems_injected = True
                st.session_state.ems_injected_file = filename.replace('.csv', '.pkl')
                st.session_state.ems_injection_success = True
                logger.info(f"Sucesso: Perfil técnico injetado em {save_path_pkl}")
            except Exception as e:
                st.session_state.ems_injection_error = str(e)
                logger.error(f"Erro ao salvar arquivo de injeção Pickle: {e}")

    # --- IDENTIFICAÇÃO DO PROJETO ---

    # --- IDENTIFICAÇÃO DO PROJETO ---
    c_id1, c_id2 = st.columns(2)
    cliente = c_id1.text_input("👤 Nome do Cliente", value=st.session_state.get('ems_cliente', ""), placeholder="Ex: LEDAX-BESS")
    projeto = c_id2.text_input("🏷️ Nome do Projeto", value=st.session_state.get('ems_projeto', ""), placeholder="Ex: Expansão Planta A")
    
    st.session_state.ems_cliente = cliente
    st.session_state.ems_projeto = projeto

    # Inicializa o Manager (agnóstico)
    ems_manager = EMSManager(
        strategies=[],
        p_bess_max_w=CONFIGURACAO.bateria.P_bess,
        capacidade_nominal_wh=CONFIGURACAO.bateria.capacidade_nominal_wh
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📂 Dados de Carga")
        uploaded_file = st.file_uploader("Upload Perfil de Carga (CSV ou XLSX)", type=["csv", "xlsx"], key="ems_uploader_step")
        
        if uploaded_file is not None:
            try:
                # Determina o método de leitura pela extensão
                if uploaded_file.name.endswith('.csv'):
                    # Tenta detectar separador automático
                    df_preview = pd.read_csv(uploaded_file, nrows=0, sep=None, engine='python')
                else:
                    df_preview = pd.read_excel(uploaded_file, nrows=0)
                
                cols = df_preview.columns.tolist()
                
                c_a, c_b = st.columns(2)
                time_col = c_a.selectbox("Coluna de Tempo", cols, index=0 if len(cols) > 0 else 0)
                load_col = c_b.selectbox("Coluna de Carga", cols, index=1 if len(cols) > 1 else 0)
                
                with st.expander("🛠️ Colunas Adicionais (PFC / Qualidade)"):
                    c_fp, c_q = st.columns(2)
                    fp_col = c_fp.selectbox("Fator de Potência (Opcional)", ["Nenhum"] + cols, index=0)
                    q_col = c_q.selectbox("Reativo kVARh (Opcional)", ["Nenhum"] + cols, index=0)
                    
                    c_va, _ = st.columns(2)
                    va_col = c_va.selectbox("Potência Aparente kVAh (Opcional)", ["Nenhum"] + cols, index=0)

                    if q_col != "Nenhum":
                        st.info("💡 Se selecionado kVARh, o sistema calculará o VAr médio baseado no intervalo (dt).")
                    if va_col != "Nenhum":
                        st.info("💡 Se selecionado kVAh, o sistema calculará o VA médio baseado no intervalo (dt).")
                
                unit_type = st.radio("Unidade original", ["Potência (W/kW)", "Energia (Wh/kWh)"], index=0, horizontal=True)
                
                # Save column choices
                st.session_state.ems_unit_type = unit_type
                st.session_state.ems_time_col = time_col
                st.session_state.ems_load_col = load_col
                st.session_state.ems_fp_col = None if fp_col == "Nenhum" else fp_col
                st.session_state.ems_q_col = None if q_col == "Nenhum" else q_col
                st.session_state.ems_va_col = None if va_col == "Nenhum" else va_col
            except Exception as e:
                st.error(f"Erro ao ler cabeçalho: {e}")

    with col2:
        st.subheader("🎯 Estratégia de Despacho")
        strategy_name = st.radio("Algoritmo Principal", ["Peak Shaving", "Load Shifting", "Power Factor Correction", "Combined (LS + PS)"], index=0, horizontal=True)
        
        params = {}
        if strategy_name == "Peak Shaving":
            params['peak_limit_kw'] = st.number_input("Limite de Pico Contratado (kW)", value=100.0, step=10.0)
            c_s1, c_s2 = st.columns(2)
            params['faixa_seguranca_kw'] = c_s1.number_input("Margem Absoluta (kW)", value=0.0)
            params['faixa_seguranca_pct'] = c_s2.number_input("Margem Percentual (%)", value=0.0)
        
        elif strategy_name == "Load Shifting":
            params['limite_demanda_kw'] = st.number_input("Limite de Demanda (kW)", value=100.0)
            
            st.markdown("⏱️ **Janelas Horárias**")
            cA, cB = st.columns(2)
            params['hora_inic_carga'] = cA.number_input("Inic. Carga (h)", 0, 23, 22)
            params['hora_fim_carga'] = cB.number_input("Fim Carga (h)", 0, 23, 17)
            
            cC, cD = st.columns(2)
            params['hora_inic_descarga'] = cC.number_input("Inic. Ponta (h)", 0, 23, 18)
            params['hora_fim_descarga'] = cD.number_input("Fim Ponta (h)", 0, 23, 21)
            
            st.markdown("📅 **Localização e Feriados**")
            estados_br = ["Nenhum", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
            params['estado'] = st.selectbox("Estado (UF) para Feriados", estados_br, index=0)
            
            params['ignorar_fins_de_semana'] = st.checkbox("Ignorar Sábados e Domingos", value=True)
            custom_feriados_str = st.text_input("Feriados Locais Extras (YYYY-MM-DD)", placeholder="EX: 2024-11-20")
            params['feriados_municipais'] = [x.strip() for x in custom_feriados_str.split(',')] if custom_feriados_str.strip() else []

        elif strategy_name == "Power Factor Correction":
            params['pf_target'] = st.number_input("Fator de Potência Alvo", min_value=0.8, max_value=1.0, value=0.98, step=0.01)
            params['s_max_va'] = st.number_input("Capacidade do Inversor (VA)", min_value=1000.0, value=125000.0, step=5000.0)
            st.info("💡 Esta estratégia despacha reativos para atingir o FP alvo, limitada pela capacidade do inversor.")

        elif strategy_name == "Combined (LS + PS)":
            params['limite_demanda_kw'] = st.number_input("Limite de Pico Contratado (kW)", value=100.0, step=10.0)
            c_s1, c_s2 = st.columns(2)
            params['faixa_seguranca_kw'] = c_s1.number_input("Margem Absoluta (kW)", value=0.0)
            params['faixa_seguranca_pct'] = c_s2.number_input("Margem Percentual (%)", value=0.0)
            
            st.markdown("⏱️ **Janelas Horárias (Load Shifting)**")
            cA, cB = st.columns(2)
            params['hora_inic_carga'] = cA.number_input("Inic. Carga (h)", 0, 23, 22)
            params['hora_fim_carga'] = cB.number_input("Fim Carga (h)", 0, 23, 17)
            
            cC, cD = st.columns(2)
            params['hora_inic_descarga'] = cC.number_input("Inic. Ponta (h)", 0, 23, 18)
            params['hora_fim_descarga'] = cD.number_input("Fim Ponta (h)", 0, 23, 21)
            
            st.markdown("📅 **Localização e Feriados**")
            estados_br = ["Nenhum", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
            params['estado'] = st.selectbox("Estado (UF) para Feriados", estados_br, index=0)
            
            params['ignorar_fins_de_semana'] = st.checkbox("Ignorar Sábados e Domingos", value=True)
            custom_feriados_str = st.text_input("Feriados Locais Extras (YYYY-MM-DD)", placeholder="EX: 2024-11-20")
            params['feriados_municipais'] = [x.strip() for x in custom_feriados_str.split(',')] if custom_feriados_str.strip() else []

    st.markdown("---")
    
    if st.button("📊 Gerar Preview e Validar Estratégia", type="primary", width="stretch"):
        if uploaded_file is None:
            st.warning("Por favor, faça o upload de um arquivo antes de processar.")
            return

        with st.spinner("Vetorizando despacho comercial..."):
            try:
                uploaded_file.seek(0)
                if uploaded_file.name.endswith('.csv'):
                    # Tenta ler com separador automático ou comum em BR (;)
                    try:
                        df_full = pd.read_csv(uploaded_file, sep=None, engine='python')
                    except:
                        uploaded_file.seek(0)
                        df_full = pd.read_csv(uploaded_file, sep=';', decimal=',')
                else:
                    df_full = pd.read_excel(uploaded_file)
                
                # Identifica colunas
                time_col = st.session_state.get('ems_time_col')
                load_col = st.session_state.get('ems_load_col')
                
                if not time_col or time_col not in df_full.columns:
                    st.error(f"Coluna de tempo '{time_col}' não encontrada no arquivo. Colunas: {df_full.columns.tolist()}")
                    return
                if not load_col or load_col not in df_full.columns:
                    st.error(f"Coluna de carga '{load_col}' não encontrada no arquivo. Colunas: {df_full.columns.tolist()}")
                    return

                # Normalização de tipos para a coluna de carga
                if df_full[load_col].dtype == object:
                    # Tenta converter limpando decorações comuns (ponto como milhar, vírgula como decimal)
                    try:
                        temp_col = df_full[load_col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                        df_full[load_col] = pd.to_numeric(temp_col)
                    except Exception as e:
                        st.error(f"Não foi possível converter a coluna '{load_col}' para números. Verifique o formato. Erro: {e}")
                        return
                
                # Feriados Automáticos (Nacionais + Estaduais)
                try:
                    df_full[time_col] = pd.to_datetime(df_full[time_col])
                    anos_presentes = df_full[time_col].dt.year.unique().tolist()
                except Exception as e:
                    st.error(f"Falha ao converter coluna '{time_col}' para data/hora: {e}")
                    return
                
                estado_uf = params.get('estado', 'Nenhum')
                if estado_uf == "Nenhum":
                    feriados_br = holidays.BR(years=anos_presentes)
                else:
                    try:
                        feriados_br = holidays.BR(years=anos_presentes, subdivision=estado_uf)
                    except:
                        feriados_br = holidays.BR(years=anos_presentes, state=estado_uf)
                
                lista_feriados = list(feriados_br.keys())
                st.session_state.ems_holidays_list = lista_feriados # Armazena para o diagnostico
                
                if strategy_name == "Load Shifting":
                    ems_manager.strategies = [LoadShiftingStrategy()]
                    if params.get('feriados_municipais'):
                        try:
                            custom_dates = pd.to_datetime(params['feriados_municipais']).date.tolist()
                            lista_feriados.extend(custom_dates)
                        except: pass
                    
                    kwargs = {
                        'hora_inicio_carga': params['hora_inic_carga'], 'hora_fim_carga': params['hora_fim_carga'],
                        'hora_inicio_descarga': params['hora_inic_descarga'], 'hora_fim_descarga': params['hora_fim_descarga'],
                        'limite_demanda_kw': params['limite_demanda_kw'], 'ignorar_fins_de_semana': params['ignorar_fins_de_semana'],
                        'feriados': lista_feriados
                    }
                elif strategy_name == "Peak Shaving":
                    ems_manager.strategies = [PeakShavingStrategy()]
                    kwargs = {
                        'limite_demanda_kw': params['peak_limit_kw'],
                        'faixa_seguranca_kw': params['faixa_seguranca_kw'],
                        'faixa_seguranca_pct': params['faixa_seguranca_pct']
                    }
                elif strategy_name == "Power Factor Correction":
                    ems_manager.strategies = [PowerFactorCorrectionStrategy()]
                    kwargs = {
                        'pf_target': params['pf_target'],
                        's_max_va': params['s_max_va']
                    }
                elif strategy_name == "Combined (LS + PS)":
                    ems_manager.strategies = [CombinedStrategyLSPS()]
                    if params.get('feriados_municipais'):
                        try:
                            custom_dates = pd.to_datetime(params['feriados_municipais']).date.tolist()
                            lista_feriados.extend(custom_dates)
                        except: pass
                    
                    kwargs = {
                        'limite_demanda_kw': params['limite_demanda_kw'],
                        'hora_inicio_carga': params['hora_inic_carga'], 'hora_fim_carga': params['hora_fim_carga'],
                        'hora_inicio_descarga': params['hora_inic_descarga'], 'hora_fim_descarga': params['hora_fim_descarga'],
                        'faixa_seguranca_kw': params['faixa_seguranca_kw'],
                        'faixa_seguranca_pct': params['faixa_seguranca_pct'],
                        'ignorar_fins_de_semana': params['ignorar_fins_de_semana'],
                        'feriados': lista_feriados
                    }
                
                # Pass explicit column selection for PFC if available
                if st.session_state.get('ems_fp_col'):
                    kwargs['fp_col'] = st.session_state.ems_fp_col
                if st.session_state.get('ems_q_col'):
                    kwargs['q_col'] = st.session_state.ems_q_col
                if st.session_state.get('ems_va_col'):
                    kwargs['va_col'] = st.session_state.ems_va_col
                
                # Pass energy unit conversion flag
                kwargs['is_energy'] = (st.session_state.get('ems_unit_type') == "Energia (Wh/kWh)")

                df_result = ems_manager.run(df_full, time_col=time_col, load_col=load_col, **kwargs)
                st.session_state.ems_preview_result = df_result
                st.session_state.ems_params_used = params
                st.session_state.ems_strategy_used = strategy_name
                st.session_state.ems_active = True
                st.success("✅ Intenção de Despacho Gerada!")
            except Exception as e:
                # Log detailed error for debugging if needed
                logger.error(f"Critical error in Step 1 Processing: {e}", exc_info=True)
                st.error(f"Falha inesperada no processamento: {e}")

    if st.session_state.get('ems_preview_result') is not None:
        df_res = st.session_state.ems_preview_result
        
        # REQ-08 UI Warning for auto-conversion or auto-scaling
        if getattr(df_res, 'attrs', {}).get('conversion_applied'):
            st.warning(f"⚠️ **Conversão de Unidade Automática (REQ-08):** Detectamos que a coluna '{st.session_state.ems_load_col}' continha valores em formato de Energia. O sistema converteu automaticamente para Potência média em Watts (W) baseando-se no intervalo temporal (dt).")
        elif getattr(df_res, 'attrs', {}).get('scaling_applied'):
            st.warning(f"⚠️ **Escalonamento Automático (REQ-08):** Detectamos que a coluna '{st.session_state.ems_load_col}' continha valores em formato de kW. O sistema escalonou automaticamente os valores para Watts (W) para garantir a precisão física do simulador.")

        # --- NOVO: ANALISADOR DE CARGA (DIAGNÓSTICO AVANÇADO) ---
        time_col = st.session_state.get('ems_time_col') or df_res.columns[0]
        load_col = 'Carga_W'
        
        # Parâmetros de Ponta configurados
        p_used = st.session_state.get('ems_params_used', {})
        h_ini = p_used.get('hora_inic_descarga', 18)
        h_fim = p_used.get('hora_fim_descarga', 21)
        
        analyzer = LoadAnalyzer(df_res, time_col, load_col)
        # Reutilizamos a lista de feriados calculada anteriormente ou extraímos de algum lugar se necessário
        # Para o diagnóstico rápido, usamos a lógica de feriados nacionais se não houver lista
        metrics = analyzer.analyze(peak_start_hour=h_ini, peak_end_hour=h_fim, holidays_list=st.session_state.get('ems_holidays_list'))
        
        st.markdown("### 🔍 Diagnóstico do Perfil de Carga")
        
        # Bloqueio Crítico: Duração < 24h
        if metrics.duration_days < 0.99:
            st.error(f"❌ **Dados Insuficientes:** A planilha possui apenas {metrics.duration_days:.2f} dias de dados. O sistema exige no mínimo 24h para realizar a expansão estatística e o dimensionamento.")
            st.warning("⚠️ O botão de 'Injetar para Simulação' permanecerá bloqueado até que uma planilha válida seja carregada.")
            st.stop() # Interrompe a renderização para os passos seguintes
            
        t1, t2, t3, t4, t5 = st.tabs(["📊 Resumo Geral", "⚡ Ponta & Energia", "📅 Padrões", "⚡ Qualidade (PFC)", "⚙️ Diagnóstico"])
        
        with t1:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Pico de Carga (Pmax)", f"{metrics.p_max_w/1000:.1f} kW")
            m2.metric("Percentil 95 (P95)", f"{metrics.p95_w/1000:.1f} kW")
            m3.metric("Carga Média", f"{metrics.p_avg_w/1000:.1f} kW")
            m4.metric("Fator de Carga", f"{metrics.load_factor:.2%}")
            
            s_used = st.session_state.get('ems_strategy_used', "Load Shifting")
            limite_exibicao_w = (p_used.get('limite_demanda_kw', 0) if s_used in ["Load Shifting", "Combined (LS + PS)"] else p_used.get('peak_limit_kw', 0)) * 1000.0
            st.plotly_chart(plot_ems_dispatch_comparison(df_res, time_col, limite_w=limite_exibicao_w), width='stretch', key="chart_dispatch_main")

        with t2:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.metric("Energia Total", f"{metrics.total_energy_kwh:,.0f} kWh")
                st.metric("Consumo Médio Diário", f"{metrics.avg_daily_energy_kwh:.1f} kWh/dia")
                st.metric("Projeção Mensal (30d)", f"{metrics.est_monthly_energy_kwh:,.0f} kWh")
                st.plotly_chart(plot_peak_analysis(metrics.energy_ponta_kwh, metrics.energy_fora_ponta_kwh), width='stretch', key="chart_peak_analysis")
            with c2:
                st.metric("Pico na Ponta", f"{metrics.p_max_ponta_w/1000:.1f} kW")
                st.metric("Participação na Ponta", f"{metrics.pct_energy_ponta:.1%}")
                st.info(f"Horário de Ponta considerado: {h_ini:02d}h às {h_fim:02d}h (Exceto Fins de Semana e Feriados).")
                st.plotly_chart(plot_load_frequency_histogram(df_res, load_col), width='stretch', key="chart_load_hist")

        with t3:
            st.plotly_chart(plot_load_heatmap(df_res, time_col, load_col), width='stretch', key="chart_load_heatmap")
            st.caption("O mapa de calor acima mostra a média de consumo para cada hora do dia agrupada por dia da semana.")

            st.plotly_chart(plot_energy_balance(df_res, time_col), width='stretch', key="chart_energy_balance_t3")

        with t4:
            st.subheader("⚡ Qualidade de Energia e Reativos")
            st.markdown("Análise da compensação de reativos e melhoria do Fator de Potência.")
            
            # Metrics for PF
            p_adj = df_res['Carga_Ajustada_W']
            q_adj = df_res['Carga_VAr'] + df_res.get('Potencia_Reativa_Bateria_VAr', 0.0)
            s_adj = np.sqrt(p_adj**2 + q_adj**2)
            fp_adj = np.where(s_adj == 0, 1.0, p_adj / s_adj)
            
            fp_min_orig = df_res['Carga_FP'].min()
            fp_min_adj = fp_adj.min()
            
            m_q1, m_q2, m_q3 = st.columns(3)
            m_q1.metric("FP Mínimo (Original)", f"{fp_min_orig:.3f}")
            m_q2.metric("FP Mínimo (Pós-BESS)", f"{fp_min_adj:.3f}", delta=f"{fp_min_adj - fp_min_orig:.3f}")
            
            target_pf = p_used.get('pf_target', 0.98) if s_used == "Power Factor Correction" else None
            
            st.plotly_chart(plot_power_factor_comparison(df_res, time_col, pf_target=target_pf), width='stretch', key="chart_pfc_comparison")
            st.plotly_chart(plot_reactive_power_comparison(df_res, time_col), width='stretch', key="chart_reactive_power")

        with t5:
            q1, q2, q3 = st.columns(3)
            q1.metric("Intervalo (dT)", f"{metrics.dt_min:.1f} min")
            q2.metric("Duração Total", f"{metrics.duration_days:.1f} dias")
            q3.metric("Total de Pontos", f"{metrics.total_records:,}")
            
            if metrics.dt_min > 60:
                st.warning("⚠️ Resolução baixa detectada (>60 min). Os cálculos de picos podem estar subestimados.")
            
            st.plotly_chart(plot_energy_balance(df_res, time_col), width='stretch', key="chart_energy_balance_t5")

        st.markdown("---")
        
        r_col1, r_col2 = st.columns([2, 1])
        
        with r_col1:
            st.success("✅ Diagnóstico Concluído. Analise os gráficos acima antes de prosseguir.")
            
        with r_col2:
            st.markdown("#### 📥 Ações e Exportação")
            st.info("Pressione 'Injetar' para usar este perfil na simulação.")
            
            # Preparar DataFrame para exportação minimalista (4 colunas)
            orig_time_col = df_res.columns[0]
            orig_load_col = st.session_state.get('ems_load_col')
            export_cols = [orig_time_col, orig_load_col, 'Bateria_kW', 'Status']
            df_export = df_res[export_cols].copy()

            # Excel download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='EMS_Setpoint')
            
            # Filename amigável
            client_slug = st.session_state.get('ems_cliente', 'CLIENTE').replace(" ", "_").strip() or "CLIENTE"
            proj_slug = st.session_state.get('ems_projeto', 'PROJETO').replace(" ", "_").strip() or "PROJETO"
            friendly_name = f"ems_{client_slug}_{proj_slug}"

            st.download_button(
                label="📥 Planilha EMS (.xlsx)",
                data=output.getvalue(),
                file_name=f"{friendly_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='stretch'
            )
            
            if st.session_state.get('ems_injection_success'):
                st.balloons()
                st.success(f"🎉 Perfil injetado: `{st.session_state.ems_injected_file}`")
                st.session_state.ems_injection_success = False
            
            if st.session_state.get('ems_injection_error'):
                st.error(f"❌ Erro: {st.session_state.ems_injection_error}")
                st.session_state.ems_injection_error = None

            st.button(
                "🚀 Injetar para Simulação", 
                type="primary", 
                width='stretch',
                on_click=save_ems_profile
            )
