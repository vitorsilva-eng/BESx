import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Escopo necessário para ler, criar e alterar arquivos no Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    print("================================================================")
    print("   GERADOR DE TOKENS OAUTH PARA O GITHUB ACTIONS (BESx)")
    print("================================================================\n")
    print("Antes de continuar, certifique-se de que você baixou o arquivo")
    print("'client_secret_*.json' do seu projeto no Google Cloud e")
    print("salvou nesta mesma pasta com o nome exato: 'credentials.json'\n")
    
    if not os.path.exists('credentials.json'):
        print("[ERRO] Arquivo 'credentials.json' não encontrado na pasta atual.")
        return

    try:
        # Abre o navegador para o usuário fazer login com a conta do Gmail
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        print("\n✅ Sucesso! Autenticação concluída.")
        print("\n================================================================")
        print("  COPIE OS VALORES ABAIXO PARA O GITHUB SECRETS DO REPOSITÓRIO")
        print("================================================================\n")
        
        print(f"GDRIVE_CLIENT_ID:      {creds.client_id}")
        print(f"GDRIVE_CLIENT_SECRET:  {creds.client_secret}")
        print(f"GDRIVE_REFRESH_TOKEN:  {creds.refresh_token}")
        
        print("\n================================================================\n")
        print("Após salvar esses 3 valores na aba Actions Secrets do seu repositório,")
        print("a automação passará a utilizar o seu próprio espaço no Drive.")
        
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um problema durante a autenticação: {e}")

if __name__ == '__main__':
    main()
