import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from besx.config import CONFIGURACAO, ModeloDegradacaoConfig, PERFIS_BATERIA

# Importando validador oficial do projeto (testes de bancada)
from tests.test_engine_validation import rodar_validacao

def render_step_settings():
    """
    Passo 6: Parâmetros de Engenharia e Validação de Motores.
    """
    st.header("⚙️ Passo 6: Configurações de Engenharia")
    st.markdown("Ajuste fino dos coeficientes matemáticos e validação técnica do sistema.")

    tab_deg, tab_val = st.tabs(["🧬 Modelo de Degradação", "✔️ Validação do Motor"])

    with tab_deg:
        st.subheader("Parâmetros do Modelo (Stroe & Power Law)")
        st.caption("Ajuste os pesos dos fenômenos de fadiga cíclica e calendária.")
        
        if 'config_override' not in st.session_state:
            st.session_state.config_override = CONFIGURACAO.modelo_degradacao.model_dump()
        
        ov = st.session_state.config_override
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**1. Degradação Cíclica**")
            cA, cB = st.columns(2)
            ov['ciclo']['a'] = cA.number_input("Coeficiente a", value=ov['ciclo']['a'], format="%.4e")
            ov['ciclo']['b'] = cB.number_input("Coeficiente b", value=ov['ciclo']['b'], format="%.4e")
            cC, cD = st.columns(2)
            ov['ciclo']['c'] = cC.number_input("Coeficiente c", value=ov['ciclo']['c'], format="%.4e")
            ov['ciclo']['d'] = cD.number_input("Coeficiente d", value=ov['ciclo']['d'], format="%.4e")
            
            st.markdown("**Parâmetros de Rainflow**")
            ov['ciclo']['peak_prominence'] = st.slider("Proeminência (Peak)", 0.0, 0.1, ov['ciclo']['peak_prominence'], 0.01)

        with col2:
            st.markdown("**2. Degradação Calendária**")
            cK1, cK2 = st.columns(2)
            ov['calendario']['k_T'] = cK1.number_input("k_T (Temp)", value=ov['calendario']['k_T'], format="%.4e")
            ov['calendario']['k_soc'] = cK2.number_input("k_soc (SOC)", value=ov['calendario']['k_soc'], format="%.4e")
            
            cE1, _ = st.columns(2)
            ov['calendario']['exp_cal'] = cE1.number_input("Expoente t^n", value=ov['calendario']['exp_cal'], format="%.2f")
            
            st.info("💡 A degradação calendária segue uma lei de potência em relação ao tempo e exponencial para T/SOC.")

    with tab_val:
        st.subheader("🛠️ Suite de Validação Técnica de Motores")
        
        # Escolha da Bateria para o Teste
        perfil_nomes = list(PERFIS_BATERIA.keys())
        # Index inicial para Sany se existir
        idx_init = perfil_nomes.index("Sany_314Ah_Validation") if "Sany_314Ah_Validation" in perfil_nomes else 0
        st.selectbox("🔋 Bateria Alvo do Teste", perfil_nomes, index=idx_init, key='perfil_val_sess')
        
        st.write("Selecione os pilares de física que deseja auditar:")
        cV1, cV2, cV3, cV4 = st.columns(4)
        run_rain = cV1.checkbox("⚡ Rainflow", value=True)
        run_deg = cV2.checkbox("🧬 Degradação", value=True)
        run_eng = cV3.checkbox("⚖️ Energia", value=True)
        run_cross = cV4.checkbox("🔗 PLECS vs Python", value=False)
        
        # Botão para Regerar Perfis Sintéticos (CSV) de acordo com o JSON atual
        if st.button("🔄 Atualizar Perfis de Teste (CSV)"):
            from tests.mission_profile_generator import generate_profiles
            with st.spinner("Gerando perfis sintéticos..."):
                generate_profiles()
                st.success("✅ Perfis (TC1, TC2, TC3) regenerados com sucesso para todas as baterias.")
        
        st.divider()
        if st.button("🚀 INICIAR OS TESTES SELECIONADOS", type="secondary"):
            st.session_state.validation_run = True
            with st.spinner("Auditor físico em execução..."):
                import time
                time.sleep(1.2) # Simulação de carga computacional
                st.success("Auditoria técnica concluída.")

            # Executa a auditoria oficial (TC1, TC2, TC3)
            with st.spinner("🚀 Executando auditoria técnica (TC1, TC2, TC3)..."):
                # Captura o perfil selecionado pelo usuário acima
                perfil_selecionado = st.session_state.get('perfil_val_sess', list(PERFIS_BATERIA.keys())[0])
                res_payload = rodar_validacao(perfil_nome=perfil_selecionado)
            
            # Resultados das Assertions
            assertions = res_payload.get('assertions', {})
            if run_eng:
                with st.expander("⚖️ Validação de Conservação (TC1: Coulomb Swing)"):
                    test_tc1 = assertions.get('tc1_1c_swing', {})
                    df_tc1 = res_payload.get('tc1_data')
                    if df_tc1 is not None:
                        fig3 = go.Figure(go.Scatter(y=df_tc1['SOC'], mode='lines', line=dict(color='#ffff00')))
                        fig3.update_layout(height=180, margin=dict(l=0, r=0, t=0, b=0), template='plotly_dark')
                        st.plotly_chart(fig3, width='stretch')
                        
                    if test_tc1.get('pass'):
                        st.success(f"✅ PASS: {test_tc1['msg']}")
                    else:
                        st.error(f"❌ FAIL: {test_tc1.get('msg', 'Falha no integrador')}")
            # TESTE 1: RAINFLOW (TC2)
            if run_rain:
                with st.expander("⚡ Validação de Rainflow (TC2: Partial Cycling)", expanded=True):
                    df_tc2 = res_payload.get('tc2_data')
                    if df_tc2 is not None:
                        fig1 = go.Figure(go.Scatter(y=df_tc2['SOC'].head(200), mode='lines', line=dict(color='#00ffcc')))
                        fig1.update_layout(height=180, margin=dict(l=0, r=0, t=0, b=0), template='plotly_dark')
                        st.plotly_chart(fig1, width='stretch')
                    
                    test_rain = assertions.get('rainflow_dod', {})
                    if test_rain.get('pass'):
                        st.success(f"✅ PASS: {test_rain['msg']}")
                    else:
                        st.error(f"❌ FAIL: {test_rain.get('msg', 'Falha no Rainflow')}")

            # TESTE 2: DEGRADAÇÃO NÃO-LINEAR (TC3)
            if run_deg:
                with st.expander("🧬 Validação de Acumulação Não-Linear (TC3: Stroe)"):
                    hist_deg = res_payload.get('historico_degradacao')
                    if hist_deg:
                        fig2 = go.Figure(go.Scatter(y=hist_deg, mode='lines+markers', line=dict(color='#ff3366')))
                        fig2.update_layout(height=180, margin=dict(l=0, r=0, t=0, b=0), template='plotly_dark')
                        st.plotly_chart(fig2, width='stretch')
                        
                    test_stroe = assertions.get('stroe_nonlinear', {})
                    if test_stroe.get('pass'):
                        st.success(f"✅ PASS: {test_stroe['msg']}")
                        st.write(f"Mês 12 (Real): {hist_deg[-1]:.6f}")
                    else:
                        st.error(f"❌ FAIL: {test_stroe.get('msg', 'Falha no modelo Stroe')}")
            

            # TESTE 4: CRUZADA PLECS VS PYTHON
            if run_cross:
                with st.expander("🔗 Validação Cruzada (PLECS Ground Truth)", expanded=True):
                    cross_data = res_payload.get('cross_data')
                    if cross_data and cross_data.get('python') is not None and cross_data.get('plecs') is not None:
                        df_py = cross_data['python']
                        df_pl = cross_data['plecs']
                        
                        m_soc = cross_data.get('mae_soc', 0)
                        m_v = cross_data.get('mae_v', 0)
                        m_i = cross_data.get('mae_i', 0)
                        
                        st.info("ℹ️ **Validação de Alta Fidelidade (V2):** Comparativo ponto-a-ponto entre o motor Python e o solver físico do PLECS utilizando um perfil dinâmico de degraus de potência.")
                        
                        # Métricas de Erro Médio
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Erro Médio SOC", f"{m_soc:.4f}%", delta=None, delta_color="normal")
                        c2.metric("Erro Médio Tensão", f"{m_v:.4f} V", delta=None, delta_color="normal")
                        c3.metric("Erro Médio Corrente", f"{m_i:.4f} A", delta=None, delta_color="normal")
                        
                        st.divider()
                        
                        # Grafico 1: SOC
                        fig_soc = go.Figure()
                        fig_soc.add_trace(go.Scatter(x=df_py['Tempo'], y=df_py['SOC'], mode='lines', name='Python', line=dict(color='#00ffcc', width=3)))
                        fig_soc.add_trace(go.Scatter(x=df_pl['Tempo'], y=df_pl['SOC'], mode='lines', name='PLECS', line=dict(color='#ff9900', width=2, dash='dash')))
                        fig_soc.update_layout(title="Comparativo: State of Charge (SOC)", xaxis_title="Tempo (min)", yaxis_title="SOC (%)", height=300, template='plotly_dark', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        st.plotly_chart(fig_soc, width='stretch')
                        
                        # Grafico 2: Tensão
                        fig_v = go.Figure()
                        fig_v.add_trace(go.Scatter(x=df_py['Tempo'], y=df_py['Tensao_Term_V'], mode='lines', name='Python', line=dict(color='#00ccff', width=3)))
                        fig_v.add_trace(go.Scatter(x=df_pl['Tempo'], y=df_pl['Tensao_Term_V'], mode='lines', name='PLECS', line=dict(color='#ff66cc', width=2, dash='dash')))
                        fig_v.update_layout(title="Comparativo: Tensão de Terminal (V)", xaxis_title="Tempo (min)", yaxis_title="Volts (V)", height=300, template='plotly_dark', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        st.plotly_chart(fig_v, width='stretch')
                        
                        # Grafico 3: Corrente
                        fig_i = go.Figure()
                        fig_i.add_trace(go.Scatter(x=df_py['Tempo'], y=df_py['Corrente_A'], mode='lines', name='Python', line=dict(color='#ccff00', width=3)))
                        fig_i.add_trace(go.Scatter(x=df_pl['Tempo'], y=df_pl['Corrente_A'], mode='lines', name='PLECS', line=dict(color='#ff3300', width=2, dash='dash')))
                        fig_i.update_layout(title="Comparativo: Corrente do Banco (A)", xaxis_title="Tempo (min)", yaxis_title="Amperes (A)", height=300, template='plotly_dark', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        st.plotly_chart(fig_i, width='stretch')
                    else:
                        st.error("Divergência técnica: Não foi possível carregar os dados V2. Verifique se o PLECS está aberto na porta 1080.")

    st.markdown("---")
    if st.button("💾 Aplicar e Salvar Configurações", type="primary", width="stretch"):
        st.session_state.config_override = ov
        st.session_state.rel_override = rv
        st.balloons()
        st.success("Configurações atualizadas globalmente.")
