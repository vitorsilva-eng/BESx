import streamlit as st
import pandas as pd
from besx.application.ems.ems_manager import EMSManager, LoadShiftingStrategy, PeakShavingStrategy
from besx.infrastructure.logging.logger import logger

def render_ems_sidebar(ems_manager: EMSManager):
    """
    Renders the EMS configuration section in the Streamlit Sidebar.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔋 Configuração EMS")
    
    # 1. File Uploader
    uploaded_file = st.sidebar.file_uploader("Upload Perfil de Carga (CSV)", type=["csv"], key="ems_uploader")
    
    if uploaded_file is not None:
        try:
            # We read only the header first to detect columns
            df_preview = pd.read_csv(uploaded_file, nrows=0)
            cols = df_preview.columns.tolist()
            
            time_col = st.sidebar.selectbox("Coluna de Tempo", cols, index=0 if len(cols) > 0 else 0)
            load_col = st.sidebar.selectbox("Coluna de Carga (Potência/Energia)", cols, index=1 if len(cols) > 1 else 0)
            
            unit_type = st.sidebar.radio("Tipo de Unidade", ["Potência (W/kW)", "Energia (Wh/kWh)"], index=0)
            
            st.sidebar.markdown("---")
            st.sidebar.subheader("🎯 Estratégia")
            
            # REQ-10: Single strategy selection for V1
            strategy_name = st.sidebar.radio(
                "Algoritmo",
                ["Load Shifting", "Peak Shaving"],
                index=0
            )
            
            params = {}
            if strategy_name == "Peak Shaving":
                params['peak_limit_w'] = st.sidebar.number_input("Limite de Pico (W)", value=10000, step=1000)
            
            if st.sidebar.button("📊 Preview EMS", use_container_width=True):
                # Reset search pointer of the file
                uploaded_file.seek(0)
                df_full = pd.read_csv(uploaded_file)
                
                # Setup strategies in manager
                if strategy_name == "Load Shifting":
                    ems_manager.strategies = [LoadShiftingStrategy()]
                else:
                    ems_manager.strategies = [PeakShavingStrategy(peak_limit_w=params['peak_limit_w'])]
                
                with st.spinner("Processando estratégia..."):
                    try:
                        # Run EMS
                        df_result = ems_manager.run(
                            df_full, 
                            time_col=time_col, 
                            load_col=load_col,
                            is_energy=(unit_type == "Energia (Wh/kWh)")
                        )
                        # Store in session state
                        st.session_state.ems_preview_result = df_result
                        st.session_state.ems_active = True
                        st.success("Preview gerado!")
                    except Exception as e:
                        st.error(f"Erro no EMS: {e}")
                        logger.error(f"EMS Execution Error: {e}")
                        
        except Exception as e:
            st.sidebar.error(f"Erro ao ler arquivo: {e}")
    else:
        st.session_state.ems_active = False
        st.session_state.ems_preview_result = None
