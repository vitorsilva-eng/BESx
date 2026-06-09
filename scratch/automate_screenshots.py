import subprocess
import time
import os
import sys

def run_automation():
    print("Iniciando o servidor Streamlit em background...")
    # Caminho do app streamlit
    app_path = os.path.join("src", "besx", "entrypoints", "dashboard", "streamlit_app.py")
    
    # Inicializa o processo Streamlit em background na porta 8501
    # Forçando UTF-8 e desativando telemetria para garantir compatibilidade
    cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--server.port", "8501", "--server.headless", "true"]
    
    streamlit_proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Aguarda 10 segundos para inicialização completa do Streamlit
    print("Aguardando inicialização do servidor Streamlit na porta 8501...")
    time.sleep(10)
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Erro: Playwright não está instalado no ambiente.")
        streamlit_proc.terminate()
        return
        
    try:
        with sync_playwright() as p:
            print("Inicializando o navegador Chromium Headless em Widescreen Full HD (1920x1080)...")
            # Definindo viewport de alta definição para capturar telas amplas e nítidas
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            
            print("Carregando o painel: http://localhost:8501...")
            page.goto("http://localhost:8501", timeout=45000)
            time.sleep(8) # Tempo de estabilização do Streamlit e CSS
            
            # Pasta destino das imagens
            img_dir = os.path.join("docs", "images")
            os.makedirs(img_dir, exist_ok=True)
            
            # ==========================================
            # ETAPA 1: REGRAS DO LOCAL
            # ==========================================
            print("Processando Etapa 1: Regras do Local & EMS...")
            
            # Localiza o arquivo de mock para fazer upload e simular carregamento
            mock_file = os.path.join("data", "mock_profiles", "Sany_314Ah_TC2.csv")
            if os.path.exists(mock_file):
                print(f"Fazendo upload do arquivo de mock: {mock_file}...")
                file_input = page.locator("input[type='file']")
                if file_input.count() > 0:
                    file_input.first.set_input_files(mock_file)
                    time.sleep(4)
                    
                    # Clica em 'Gerar Preview e Validar Estratégia'
                    btn_preview = page.locator("button:has-text('Gerar Preview')")
                    if btn_preview.count() > 0:
                        btn_preview.first.click()
                        print("Calculando lógicas EMS e gerando gráficos Plotly...")
                        time.sleep(10) # Tempo maior para renderizar todos os 5 gráficos Plotly nas abas
            
            # Tira o print da Tela 1 em alta definição
            print("Capturando step1_rules.png...")
            page.screenshot(path=os.path.join(img_dir, "step1_rules.png"))
            
            # Injeta para a base de simulação clicando no botão principal
            btn_inject = page.locator("button:has-text('Injetar para Simulação')")
            if btn_inject.count() > 0:
                btn_inject.first.click()
                print("Perfil EMS injetado na base de dados (Pickle serializado).")
                time.sleep(4)
            
            # ==========================================
            # ETAPA 2: HARDWARE DA BATERIA
            # ==========================================
            print("Navegando para Etapa 2: Hardware da Bateria...")
            btn_step2 = page.locator("button:has-text('2. Escolha da Bateria')")
            if btn_step2.count() > 0:
                btn_step2.first.click()
                time.sleep(4)
                print("Capturando step2_battery.png...")
                page.screenshot(path=os.path.join(img_dir, "step2_battery.png"))
                
            # ==========================================
            # ETAPA 3: EXECUÇÃO DA SIMULAÇÃO
            # ==========================================
            print("Navegando para Etapa 3: Execução da Simulação...")
            btn_step3 = page.locator("button:has-text('3. Simulação Física')")
            if btn_step3.count() > 0:
                btn_step3.first.click()
                time.sleep(4)
                
                # Executa o simulador físico-químico
                # Usando o botão com o nome exato para garantir o acionamento correto
                btn_run = page.locator("button:has-text('🚀 INICIAR SIMULAÇÃO FÍSICO-QUÍMICA')")
                if btn_run.count() == 0:
                    btn_run = page.locator("button:has-text('INICIAR SIMULAÇÃO')")
                
                if btn_run.count() > 0:
                    btn_run.first.click()
                    print("Executando motor físico-químico do BESx em background...")
                    # Simulação real em andamento. Aguardamos 25 segundos para processar todos os meses
                    # e garantir a correta persistência dos resultados no diretório 'results/'
                    time.sleep(25)
                
                print("Capturando step3_simulation.png...")
                page.screenshot(path=os.path.join(img_dir, "step3_simulation.png"))
                
            # ==========================================
            # ETAPA 4: RESULTADOS
            # ==========================================
            print("Navegando para Etapa 4: Resultados da Simulação...")
            btn_step4 = page.locator("button:has-text('4. Resultados')")
            if btn_step4.count() > 0:
                btn_step4.first.click()
                print("Aguardando carregamento e compilação do dashboard de resultados no Plotly...")
                time.sleep(12) # Tempo maior para compilar os gráficos elétricos de alta amostragem
                print("Capturando step4_results.png...")
                page.screenshot(path=os.path.join(img_dir, "step4_results.png"))
                
            # ==========================================
            # ETAPA 5: COMPARATIVO A/B
            # ==========================================
            print("Navegando para Etapa 5: Comparativo A/B...")
            btn_step5 = page.locator("button:has-text('5. Comparativo A/B')")
            if btn_step5.count() > 0:
                btn_step5.first.click()
                time.sleep(5)
                
                # Realiza a multisseleção das duas últimas simulações para exibir um comparativo real
                multiselect = page.locator("[data-testid='stMultiSelect']")
                if multiselect.count() > 0:
                    print("Selecionando simulações reais no seletor A/B...")
                    try:
                        # Abre a lista suspensa
                        multiselect.first.click()
                        time.sleep(2)
                        
                        # Clica na primeira opção do dropdown
                        options = page.locator("li[role='option']")
                        if options.count() > 0:
                            options.first.click()
                            print("Selecionado cenário A...")
                            time.sleep(3)
                            
                        # Clica no multiselect novamente para abrir e escolher o segundo cenário
                        multiselect.first.click()
                        time.sleep(2)
                        options = page.locator("li[role='option']")
                        if options.count() > 0:
                            options.first.click()
                            print("Selecionado cenário B...")
                            time.sleep(4)
                    except Exception as select_err:
                        print(f"Aviso na seleção comparativa: {select_err}")
                
                print("Capturando step5_comparison.png...")
                page.screenshot(path=os.path.join(img_dir, "step5_comparison.png"))
                
            # ==========================================
            # ETAPA 6: CONFIGURAÇÕES E VALIDAÇÃO
            # ==========================================
            print("Navegando para Etapa 6: Configurações de Engenharia...")
            btn_step6 = page.locator("button:has-text('6. Configurações')")
            if btn_step6.count() > 0:
                btn_step6.first.click()
                time.sleep(4)
                
                # Roda a suite de testes elétricos transientes para exibir os gráficos pass/fail de física
                btn_testes = page.locator("button:has-text('🚀 INICIAR OS TESTES SELECIONADOS')")
                if btn_testes.count() == 0:
                    btn_testes = page.locator("button:has-text('INICIAR OS TESTES')")
                
                if btn_testes.count() > 0:
                    btn_testes.first.click()
                    print("Executando Suite de Validação Técnica de física (TC1, TC2, TC3)...")
                    time.sleep(8)
                
                print("Capturando step6_settings.png...")
                page.screenshot(path=os.path.join(img_dir, "step6_settings.png"))
                
            print("Navegador fechado com sucesso.")
            browser.close()
            
    except Exception as e:
        print(f"Erro crítico ocorrido durante a automação: {e}")
    finally:
        print("Finalizando o servidor Streamlit em background...")
        streamlit_proc.terminate()
        streamlit_proc.wait()
        
    print("Processo de geração automática de prints concluído com sucesso.")

if __name__ == "__main__":
    run_automation()
