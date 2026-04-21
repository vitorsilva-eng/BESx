import streamlit as st
import pandas as pd
import os
import sys

# --- Path Configuration ---
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# --- Internal Imports ---
from besx.config import CONFIGURACAO
from besx.infrastructure.ui.streamlit.pages.step_rules import render_step_rules
from besx.infrastructure.ui.streamlit.pages.step_battery import render_step_battery
from besx.infrastructure.ui.streamlit.pages.step_simulation import render_step_simulation
from besx.infrastructure.ui.streamlit.pages.step_results import render_step_results
from besx.infrastructure.ui.streamlit.pages.step_comparison import render_step_comparison
from besx.infrastructure.ui.streamlit.pages.step_settings import render_step_settings

# --- Page Setup ---
st.set_page_config(
    page_title="BESx Simulation Wizard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Global CSS (Kinetic Blueprint Styles) ---
st.markdown("""
<style>
    /* Metric and General Styles */
    [data-testid="stMetricValue"] { font-size: 24px; font-weight: 700; color: #00ffcc; }
    .stMetric { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 15px; }
    
    /* Sidebar Step Cards Styling */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        margin-bottom: -10px;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 25px 15px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: left;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        transition: all 0.3s ease;
        height: auto;
        min-height: 70px;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: #00ffcc;
        background: rgba(0, 255, 204, 0.05);
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.1);
    }

    /* Active State Class (Simulated via Label Prefix in Logic) */
    .active-card {
        border-color: #00ffcc !important;
        background: rgba(0, 255, 204, 0.1) !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'nav_step' not in st.session_state: st.session_state.nav_step = "📋 1. Regras do Local"
if 'sim_results' not in st.session_state: st.session_state.sim_results = pd.DataFrame()
if 'sim_status' not in st.session_state: st.session_state.sim_status = "idle"
if 'config_override' not in st.session_state: st.session_state.config_override = CONFIGURACAO.modelo_degradacao.model_dump()
if 'ems_injected' not in st.session_state: st.session_state.ems_injected = False
if 'ems_cliente' not in st.session_state: st.session_state.ems_cliente = ""
if 'ems_projeto' not in st.session_state: st.session_state.ems_projeto = ""

# --- Navigation (Premium Cards Sidebar) ---
st.sidebar.title("🔋 BESx Simulator")
st.sidebar.markdown("*Kinetic Blueprint Interface*")
st.sidebar.markdown("---")

# Definição dos Passos e Status
steps_config = [
    {"id": "step1", "label": "📋 1. Regras do Local", "status": "ems_injected"},
    {"id": "step2", "label": "🔋 2. Escolha da Bateria", "status": ""},
    {"id": "step3", "label": "⚙️ 3. Simulação Física", "status": "sim_status"},
    {"id": "step4", "label": "📊 4. Resultados", "status": ""},
    {"id": "step5", "label": "📈 5. Comparativo A/B", "status": ""},
    {"id": "step6", "label": "🛠️ 6. Configurações", "status": ""}
]

# Achar índice do passo ativo para o CSS
active_idx = 0
for i, s in enumerate(steps_config):
    if s["label"] == st.session_state.nav_step:
        active_idx = i + 1
        break

# Injetar CSS Dinâmico para o Glow do Card Ativo
st.markdown(f"""
<style>
    /* Alvo: O n-ésimo filho que contém um botão na sidebar (Título, Subtitle, Divider = 3 primeiros) */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-of-type({active_idx + 3}) button {{
        border-color: #00ffcc !important;
        background: rgba(0, 255, 204, 0.1) !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.15) !important;
        transform: translateX(10px);
    }}
</style>
""", unsafe_allow_html=True)

# Callback de Navegação (Mais robusto que st.rerun no loop)
def change_step(new_step):
    st.session_state.nav_step = new_step

for step in steps_config:
    # Lógica de Checkmark de conclusão
    status_suffix = ""
    if step["status"] == "ems_injected" and st.session_state.ems_injected:
        status_suffix = "  ✅"
    elif step["status"] == "sim_status" and st.session_state.sim_status == "finished":
        status_suffix = "  ✅"
    
    # Gerar botão sem prefixos que mudam o label (para estabilidade de re-render)
    button_label = f"{step['label']}{status_suffix}"
    
    st.sidebar.button(
        button_label, 
        key=f"nav_btn_{step['id']}", 
        width='stretch',
        on_click=change_step,
        args=(step["label"],)
    )

st.sidebar.markdown("---")

# --- Step Dispatcher ---
selected_step = st.session_state.nav_step

if "1. Regras" in selected_step:
    render_step_rules()
elif "2. Escolha" in selected_step:
    render_step_battery()
elif "3. Simulação" in selected_step:
    render_step_simulation()
elif "4. Resultados" in selected_step:
    render_step_results()
elif "5. Comparativo" in selected_step:
    render_step_comparison()
elif "6. Configurações" in selected_step:
    render_step_settings()

# --- Footer ---
st.sidebar.markdown("---")
# --- DEBUG SECTION ---
with st.sidebar.expander("🛠️ Diagnóstico do Sistema"):
    st.write(f"Injetado: `{st.session_state.ems_injected}`")
    st.write(f"Arquivo: `{st.session_state.get('ems_injected_file', 'Vazio')}`")
    st.write(f"Status Sim: `{st.session_state.sim_status}`")

st.sidebar.caption("BESx Dashboard v2.0 | Option 2 Nav Active")
