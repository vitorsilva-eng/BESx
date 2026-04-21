import streamlit as st
from besx.config import PERFIS_BATERIA

def render_step_battery():
    """
    Passo 2: Configuração Física da Bateria e Limites Operacionais.
    """
    st.header("🔋 Passo 2: Hardware da Bateria")
    st.markdown("Defina as características físicas e as proteções de segurança da sua bateria.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🛠️ Modelo e Capacidade")
        battery_prof = st.selectbox(
            "Selecione o Perfil da Bateria", 
            list(PERFIS_BATERIA.keys()), 
            index=0,
            help="Modelos pré-configurados com curvas OCV e resistência interna mapeadas."
        )
        
        # Get selected profile data
        profile = PERFIS_BATERIA[battery_prof]
        
        st.markdown("---")
        n_unid = st.number_input(
            "Quantidade de BESS em Paralelo", 
            min_value=1, 
            max_value=100, 
            value=st.session_state.get('battery_config', {}).get('n_unidades', 1),
            help="Define quantas unidades idênticas operam em paralelo, dividindo a corrente e somando a capacidade/potência."
        )
        
        pot_total_kw = (profile.P_bess * n_unid) / 1000.0
        cap_total_kwh = (profile.capacidade_nominal_wh * n_unid) / 1000.0
        
        st.info(f"**Resumo Técnico do Conjunto:**\n\n"
                f"- **Química:** {profile.quimica}\n"
                f"- **Capacidade Total:** {cap_total_kwh:.1f} kWh\n"
                f"- **Potência Total:** {pot_total_kw:.1f} kW\n"
                f"- **Configuração:** {profile.Ns}S / {profile.Np * n_unid}P (Strings Totais)")

    with col2:
        st.subheader("🛡️ Limites de Segurança")
        
        st.markdown("**Estado de Carga (SOC)**")
        soc_range = st.slider("Faixa de Operação (%)", 0, 100, (20, 80), help="A bateria nunca sairá desta faixa durante a simulação.")
        
        st.markdown("**Condições Térmicas**")
        t_cyc = st.slider("Temperatura de Operação (°C)", 0, 70, 35, help="Temperatura média das células durante ciclos de carga/descarga.")
        t_idl = st.slider("Temperatura de Repouso (°C)", 0, 70, 25, help="Temperatura das células enquanto a bateria aguarda despacho.")

    st.markdown("---")
    
    # Save to session state for simulation use
    st.session_state.battery_config = {
        "profile_name": battery_prof,
        "n_unidades": n_unid,
        "soc_min": soc_range[0] / 100.0,
        "soc_max": soc_range[1] / 100.0,
        "t_cycle_c": t_cyc,
        "t_idle_c": t_idl
    }
    
    st.success("✅ Configurações de hardware salvas. Prossiga para a Simulação.")
