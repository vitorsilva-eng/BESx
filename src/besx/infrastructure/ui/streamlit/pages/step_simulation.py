import streamlit as st
import time
import os
from besx.infrastructure.ui.streamlit.utils.render_utils import render_glass_battery
from besx.config import CONFIGURACAO, ModeloDegradacaoConfig, PATH_DATABASE

def render_step_simulation():
    """
    Passo 3: Configuração do Motor e Execução da Simulação.
    """
    import pandas as pd
    from besx.application.simulation import SimulationManager

    st.header("⚙️ Passo 3: Execução da Simulação")
    st.markdown("Escolha o motor de cálculo e inicie o processamento da jornada da bateria.")

    if not st.session_state.get('ems_injected'):
        st.warning("⚠️ Aviso: Você ainda não injetou um perfil EMS no Passo 1. A simulação usará o perfil padrão da base de dados.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🚀 Motor (Backend)")
        is_cloud = os.environ.get("HOSTNAME", "").startswith("streamlit") or "STREAMLIT_SERVER_PORT" in os.environ
        
        if is_cloud:
            st.info("☁️ Rodando na nuvem: PLECS indisponível.")
            backend = st.radio("Escolha o Motor", ["python"], horizontal=True, disabled=True)
        else:
            backend = st.radio("Escolha o Motor", ["plecs", "python"], index=1, horizontal=True)
            
        st.markdown("**Período de Simulação**")
        tipo_duracao = st.radio("Unidade", ["Anos", "Meses"], horizontal=True)
        if tipo_duracao == "Anos":
            anos_sim = st.slider("Duração (Anos)", 1, 15, 1)
            meses_total = None # Manager usará anos_sim * 12
        else:
            meses_total = st.slider("Duração (Meses)", 1, 12, 6)
            anos_sim = 1 # Dummy value

    with col2:
        st.subheader("🎯 Opções Avançadas")
        sim_eol_mode = st.toggle("Simular até Fim de Vida (80% SOH)", value=False)
        st.caption("No modo EOL, a simulação ignora o período e roda até a bateria 'morrer'.")

    st.markdown("---")

    # --- NOVO: SELEÇÃO DE ARQUIVO DA BASE DE DADOS ---
    st.subheader("📊 Seleção de Dados")
    db_files = [f for f in os.listdir(PATH_DATABASE) if f.endswith(('.mat', '.csv', '.pkl')) and not f.startswith('.')]
    db_files = sorted(db_files)
    
    # Prioriza o arquivo injetado no Passo 1 se existir
    injected_file = st.session_state.get('ems_injected_file')
    has_injection = st.session_state.get('ems_injected', False)
    
    if has_injection and injected_file:
        st.success(f"📍 Perfil EMS injetado detectado: `{injected_file}`")
        try:
            def_idx = db_files.index(injected_file)
        except:
            def_idx = 0
    else:
        st.warning("⚠️ Nenhum perfil injetado recentemente. Selecione um arquivo da base de dados abaixo.")
        def_idx = 0
        
    data_file_selected = st.selectbox(
        "Escolha o Perfil de Carga para Simulação", 
        db_files, 
        index=def_idx if db_files else 0,
        help="Escolha entre perfis Pickle (.pkl), legados (.mat) ou fontes CSV",
        key="sim_data_file"
    )

    st.markdown("---")

    # Placeholder para métricas ao vivo
    metrics_placeholder = st.empty()
    progress_bar = st.progress(0)
    status_msg = st.empty()

    def live_callback(df_soc, res_mes, df_in):
        # Update Session State globally
        if st.session_state.get('sim_results') is None or st.session_state.sim_results.empty:
            st.session_state.sim_results = pd.DataFrame([res_mes])
        else:
            st.session_state.sim_results = pd.concat([st.session_state.sim_results, pd.DataFrame([res_mes])], ignore_index=True)
        
        st.session_state.curr_soc = df_soc
        st.session_state.curr_input = df_in
        
        mes = res_mes['mes']
        total = res_mes['total_meses']
        progress_bar.progress(mes / total if total > 0 else 1.0)
        status_msg.markdown(f"**Processando:** Mês {mes} de {total}")
        
        # Display Live Metrics de forma mais eficiente
        with metrics_placeholder.container():
            cM1, cM2 = st.columns([1, 4])
            with cM1:
                render_glass_battery(res_mes['capacidade_restante'])
            with cM2:
                # Performance calc
                start_time = st.session_state.get('start_sim_time', time.time())
                elapsed = time.time() - start_time
                speed = mes / elapsed if elapsed > 0 else 0
                eta = (total - mes) / speed if speed > 0 else 0
                
                st.markdown(f"### 📊 Mês {mes} / {total}")
                st.markdown(f"**Saúde (SOH):** `{res_mes['capacidade_restante']:.2f}%`  \n"
                            f"**Ciclos (EFC):** `{st.session_state.sim_results['EFC_Ciclos_Equivalentes'].iloc[-1]:.1f}`")
                
                st.markdown(f"<p style='font-size: 13px; color: grey;'>⚡ Velocidade: <b>{speed:.1f} meses/s</b> | ⏳ Restam: <b>{int(eta)}s</b></p>", unsafe_allow_html=True)

    if st.button("🚀 INICIAR SIMULAÇÃO FÍSICO-QUÍMICA", type="primary", width="stretch"):
        st.session_state.sim_status = "running"
        st.session_state.start_sim_time = time.time()
        st.session_state.sim_results = pd.DataFrame()
        st.session_state.throughput = 0.0
        st.session_state.energy_charge = 0.0
        st.session_state.energy_discharge = 0.0

        # Build Config
        cfg = CONFIGURACAO.model_copy(deep=True)
        
        # Get data from Step 2
        bat_cfg = st.session_state.get('battery_config', {})
        perf_name = bat_cfg.get('profile_name', list(st.session_state.get('PERFIS_BATERIA', {}).keys())[0] if 'PERFIS_BATERIA' in st.session_state else 'LFP_Generic')
        
        from besx.config import PERFIS_BATERIA
        cfg.bateria = PERFIS_BATERIA[perf_name].model_copy(deep=True)
        cfg.bateria.Tbat_kelvin = bat_cfg.get('t_cycle_c', 35) + 273.15
        cfg.bateria.Tbat_kelvin_idle = bat_cfg.get('t_idle_c', 25) + 273.15
        cfg.bateria.soc_min = bat_cfg.get('soc_min', 0.2)
        cfg.bateria.soc_max = bat_cfg.get('soc_max', 0.8)
        
        # Período de Simulação e Unidades
        cfg.simulacao.n_unidades = bat_cfg.get('n_unidades', 1)
        
        if tipo_duracao == "Anos":
            cfg.simulacao.ANOS_SIMULACAO = anos_sim
            cfg.simulacao.MESES_SIMULACAO = None
        else:
            cfg.simulacao.ANOS_SIMULACAO = 1 # Dummy
            cfg.simulacao.MESES_SIMULACAO = meses_total
        
        # OTIMIZAÇÃO: Desativar logs detalhados (I/O) no Passo 3 para mais velocidade
        cfg.relatorio.gerar_validacao_detalhada = False
        
        # Usa o arquivo selecionado no selectbox (via key="sim_data_file")
        data_file = st.session_state.get('sim_data_file', data_file_selected)
        
        with st.spinner("Motor Termodinâmico em Execução..."):
            try:
                sim = SimulationManager(
                    cfg, backend=backend, data_file=data_file,
                    on_mes_complete=live_callback, sim_until_eol=sim_eol_mode
                )
                
                status_msg.info("🔍 Analisando e fatiando perfil de carga...")
                sim.run()
                
                if st.session_state.get('sim_results') is not None and not st.session_state.sim_results.empty:
                    st.session_state.sim_status = "finished"
                    st.success("🎉 Simulação concluída! Veja os resultados detalhados no Passo 4.")
                    st.balloons()
                else:
                    st.error("❌ A simulação terminou sem gerar resultados. Verifique se o perfil EMS injetado contém dados suficientes (mínimo de 6 dias para compor um mês).")
                    st.session_state.sim_status = "error"
            except Exception as e:
                st.error(f"Erro crítico na simulação: {e}")
                logger.error(f"Simul-Error: {e}", exc_info=True)
                st.session_state.sim_status = "error"
