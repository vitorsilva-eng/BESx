import os
import sys
import time
import socket
import subprocess
import json
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÃO DE CAMINHOS ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "scratch", "audit_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Usar a porta 8509 para evitar conflitos com sessões Streamlit em execução
PORT = 8509
URL = f"http://localhost:{PORT}"

# Arquivos de log do Streamlit
STDOUT_LOG = os.path.join(RESULTS_DIR, "streamlit_stdout.log")
STDERR_LOG = os.path.join(RESULTS_DIR, "streamlit_stderr.log")

def safe_print(text):
    """Função de impressão resiliente para evitar UnicodeEncodeError no console Windows."""
    try:
        encoding = sys.stdout.encoding or 'utf-8'
        print(text.encode(encoding, errors='replace').decode(encoding))
    except Exception:
        try:
            print(text.encode('cp1252', errors='replace').decode('cp1252'))
        except Exception:
            print(text.encode('ascii', errors='replace').decode('ascii'))

def is_port_open(port):
    """Verifica se a porta local está aberta."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

def start_streamlit():
    """Inicia o servidor Streamlit em segundo plano se não estiver rodando."""
    if is_port_open(PORT):
        safe_print(f"[INFO] Servidor Streamlit já detectado na porta {PORT}.")
        return None, None, None
    
    safe_print(f"[INFO] Iniciando Streamlit em segundo plano na porta {PORT}...")
    
    # Determina o Python a ser usado
    conda_py = os.path.join(PROJECT_ROOT, ".conda", "python.exe")
    python_exe = conda_py if os.path.exists(conda_py) else "python"
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(PROJECT_ROOT, "src")
    
    cmd = [
        python_exe, "-m", "streamlit", "run", 
        os.path.join(PROJECT_ROOT, "src", "besx", "entrypoints", "dashboard", "streamlit_app.py"),
        "--server.port", str(PORT),
        "--server.headless", "true"
    ]
    
    # Abre os arquivos de log
    stdout_file = open(STDOUT_LOG, "w", encoding="utf-8")
    stderr_file = open(STDERR_LOG, "w", encoding="utf-8")
    
    process = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        env=env,
        stdout=stdout_file,
        stderr=stderr_file
    )
    
    # Aguarda a porta abrir
    max_retries = 30
    for i in range(max_retries):
        if is_port_open(PORT):
            safe_print(f"[OK] Streamlit iniciado com sucesso no processo PID={process.pid}.")
            time.sleep(3)  # Tempo extra de estabilização
            return process, stdout_file, stderr_file
        time.sleep(1)
        
    safe_print("[ERRO] Falha ao iniciar o Streamlit dentro do limite de tempo.")
    process.kill()
    stdout_file.close()
    stderr_file.close()
    sys.exit(1)

def run_audit():
    """Executa o script de auditoria do Playwright."""
    safe_print("==================================================")
    safe_print("        INICIANDO AUDITORIA DA INTERFACE          ")
    safe_print("==================================================")
    
    # Inicia o Streamlit se necessário
    streamlit_process, stdout_file, stderr_file = start_streamlit()
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "steps": [],
        "success": True
    }
    
    try:
        with sync_playwright() as p:
            safe_print("[INFO] Inicializando navegador Chromium...")
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                safe_print(f"[AVISO] Falha ao iniciar Chromium: {e}. Tentando instalar os navegadores...")
                os.system("playwright install chromium")
                browser = p.chromium.launch(headless=True)
                
            page = browser.new_page()
            
            # Coletor de erros de console e de página
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: console_errors.append(str(err)))
            
            safe_print(f"[INFO] Acessando {URL}...")
            page.goto(URL)
            
            # AGUARDAR O STREAMLIT TERMINAR O LOADING SKELETON
            safe_print("[INFO] Aguardando o botão 'Regras do Local' ficar visível na barra lateral...")
            try:
                page.locator("button:has-text('Regras do Local')").wait_for(state="visible", timeout=35000)
                safe_print("[OK] Dashboard renderizado e pronto para interação.")
            except Exception as e:
                safe_print(f"[ERRO] Timeout aguardando o carregamento da UI: {e}")
                page.screenshot(path=os.path.join(RESULTS_DIR, "timeout_state.png"))
                raise e
            
            time.sleep(2)  # Tempo para renderização inicial estabilizar
            
            steps = [
                {"id": "step1", "name": "1. Regras do Local", "search_text": "Regras do Local", "title_keyword": "Passo 1"},
                {"id": "step2", "name": "2. Escolha da Bateria", "search_text": "Escolha da Bateria", "title_keyword": "Passo 2"},
                {"id": "step3", "name": "3. Simulação Física", "search_text": "Simulação Física", "title_keyword": "Passo 3"},
                {"id": "step4", "name": "4. Resultados", "search_text": "Resultados", "title_keyword": "Passo 4"},
                {"id": "step5", "name": "5. Comparativo A/B", "search_text": "Comparativo", "title_keyword": "Passo 5"},
                {"id": "step6", "name": "6. Configurações", "search_text": "Configurações", "title_keyword": "Passo 6"}
            ]
            
            for step in steps:
                step_name = step["name"]
                step_id = step["id"]
                safe_print(f"\n[INFO] Auditando Passo: {step_name}...")
                
                # Acha o botão na barra lateral
                btn_locator = page.locator(f"section[data-testid='stSidebar'] button:has-text('{step['search_text']}')")
                if btn_locator.count() == 0:
                    btn_locator = page.locator(f"button:has-text('{step['search_text']}')")
                
                if btn_locator.count() == 0:
                    safe_print(f"[ERRO] Botão para o passo '{step_name}' não encontrado.")
                    report["steps"].append({
                        "step": step_name,
                        "status": "NOT_FOUND",
                        "errors": ["Botão de navegação não encontrado."]
                    })
                    report["success"] = False
                    continue
                
                # NAVEGAÇÃO RESILIENTE COM RETENTATIVAS DE CLIQUE E VERIFICAÇÃO ATIVA DO DOM
                max_clicks = 4
                clicked_ok = False
                page_titles = []
                
                for attempt in range(max_clicks):
                    safe_print(f"   -> Tentativa de clique {attempt+1}/{max_clicks}...")
                    btn_locator.first.click(force=True)
                    time.sleep(4.0)  # Tempo de espera generoso para re-run estável
                    
                    # Extrai títulos da tela principal
                    h1_elements = page.locator("h1, h2")
                    page_titles = []
                    for i in range(h1_elements.count()):
                        title_text = h1_elements.nth(i).inner_text().strip()
                        if title_text:
                            page_titles.append(title_text)
                    
                    # Verifica se navegou para a página correta identificando o termo de busca no título
                    if any(step['title_keyword'] in t for t in page_titles):
                        clicked_ok = True
                        break
                    else:
                        safe_print(f"      [AVISO] A navegação para {step_name} ainda não foi concluída. (Títulos: {page_titles}). Retentando...")
                        # Dá um tempo de escape caso o Streamlit esteja muito ocupado
                        time.sleep(2.0)
                
                safe_print(f"   -> Títulos detectados na página: {page_titles}")
                
                # Tira captura de tela
                screenshot_path = os.path.join(RESULTS_DIR, f"{step_id}.png")
                page.screenshot(path=screenshot_path)
                
                # Procura por stException ou caixas de erro do Streamlit
                exceptions = page.locator("div[data-testid='stException']")
                error_messages = []
                
                if exceptions.count() > 0:
                    safe_print(f"[ERRO] stException encontrada no {step_name}!")
                    for i in range(exceptions.count()):
                        err_text = exceptions.nth(i).inner_text()
                        error_messages.append(err_text)
                        safe_print(f"      Exceção: {err_text}")
                    report["success"] = False
                
                # Procura por elementos stAlert contendo erro
                alerts = page.locator("div[data-testid='stAlert']:has-text('Erro')")
                if alerts.count() > 0:
                    safe_print(f"[ERRO] stAlert de erro encontrado no {step_name}!")
                    for i in range(alerts.count()):
                        alert_text = alerts.nth(i).inner_text()
                        error_messages.append(alert_text)
                        safe_print(f"      Alerta: {alert_text}")
                    report["success"] = False
                
                # Se após todas as tentativas a página de fato não mudou de título principal
                if not clicked_ok:
                    safe_print(f"[ERRO] A página de fato falhou em mudar para o {step_name}.")
                    error_messages.append("Falha técnica de navegação do Streamlit (a página não re-renderizou).")
                    report["success"] = False
                
                # Coleta erros específicos do console acumulados até agora
                current_console_errors = list(console_errors)
                console_errors.clear()
                
                step_status = "PASS" if not error_messages and not current_console_errors and clicked_ok else "FAIL"
                
                report["steps"].append({
                    "step": step_name,
                    "status": step_status,
                    "titles": page_titles,
                    "errors": error_messages,
                    "console_errors": current_console_errors,
                    "screenshot": f"scratch/audit_results/{step_id}.png"
                })
                
                safe_print(f"[STATUS] {step_name}: {step_status}")
            
            browser.close()
            
    except Exception as e:
        safe_print(f"[ERRO CRÍTICO] Falha ao rodar a automação: {e}")
        report["success"] = False
        report["critical_error"] = str(e)
        
    finally:
        if streamlit_process:
            safe_print("[INFO] Encerrando o servidor Streamlit iniciado...")
            streamlit_process.kill()
            stdout_file.close()
            stderr_file.close()
            
    report_path = os.path.join(RESULTS_DIR, "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    safe_print("\n==================================================")
    safe_print("              AUDITORIA FINALIZADA                ")
    safe_print("==================================================")
    safe_print(f"Relatório salvo em: {report_path}")
    safe_print(f"Resultado Geral: {'SUCESSO' if report['success'] else 'FALHA'}")
    safe_print("==================================================")

if __name__ == "__main__":
    run_audit()
