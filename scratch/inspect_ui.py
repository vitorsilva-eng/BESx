import os
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "scratch", "audit_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

URL = "http://localhost:8501"

def inspect():
    with sync_playwright() as p:
        print("[INFO] Inicializando navegador...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"[INFO] Acessando {URL}...")
        page.goto(URL)
        
        try:
            page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=10000)
            print("[OK] Container principal encontrado.")
        except Exception as e:
            print(f"[AVISO] Timeout aguardando o container: {e}")
            
        # Espera um pouco mais para renderizar tudo
        page.wait_for_timeout(3000)
        
        # Tira screenshot inicial
        screenshot_path = os.path.join(RESULTS_DIR, "initial_page.png")
        page.screenshot(path=screenshot_path)
        print(f"[OK] Screenshot inicial salvo em: {screenshot_path}")
        
        # Lista todos os botões
        buttons = page.locator("button")
        count = buttons.count()
        print(f"\n[INFO] Encontrados {count} botões na página:")
        for i in range(count):
            btn = buttons.nth(i)
            text = btn.inner_text().strip()
            testid = btn.get_attribute("data-testid")
            print(f"  Botão {i}: Text='{text}' | data-testid='{testid}'")
            
        # Lista toda a barra lateral se houver
        sidebar = page.locator("section[data-testid='stSidebar']")
        if sidebar.count() > 0:
            print("\n[INFO] Conteúdo de texto da barra lateral:")
            print(sidebar.first.inner_text())
        else:
            print("\n[AVISO] Barra lateral não encontrada via section[data-testid='stSidebar'].")
            
        browser.close()

if __name__ == "__main__":
    inspect()
