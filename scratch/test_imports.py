import os
import sys

# Configura o PYTHONPATH para a pasta src
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(PROJECT_ROOT, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_imports():
    print("=== TESTANDO IMPORTAÇÕES DE PÁGINAS ===")
    
    try:
        print("[INFO] Importando step_rules...")
        from besx.infrastructure.ui.streamlit.pages.step_rules import render_step_rules
        print("[OK] step_rules importada.")
    except Exception as e:
        print(f"[ERRO] Falha ao importar step_rules: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("[INFO] Importando step_battery...")
        from besx.infrastructure.ui.streamlit.pages.step_battery import render_step_battery
        print("[OK] step_battery importada.")
    except Exception as e:
        print(f"[ERRO] Falha ao importar step_battery: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("[INFO] Importando step_simulation...")
        from besx.infrastructure.ui.streamlit.pages.step_simulation import render_step_simulation
        print("[OK] step_simulation importada.")
    except Exception as e:
        print(f"[ERRO] Falha ao importar step_simulation: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("[INFO] Importando step_results...")
        from besx.infrastructure.ui.streamlit.pages.step_results import render_step_results
        print("[OK] step_results importada.")
    except Exception as e:
        print(f"[ERRO] Falha ao importar step_results: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("[INFO] Importando step_comparison...")
        from besx.infrastructure.ui.streamlit.pages.step_comparison import render_step_comparison
        print("[OK] step_comparison importada.")
    except Exception as e:
        print(f"[ERRO] Falha ao importar step_comparison: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("[INFO] Importando step_settings...")
        from besx.infrastructure.ui.streamlit.pages.step_settings import render_step_settings
        print("[OK] step_settings importada.")
    except Exception as e:
        print(f"[ERRO] Falha ao importar step_settings: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
