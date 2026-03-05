import xmlrpc.client
import time

print("Iniciando teste de conexão com o servidor PLECS (via --server)...")

# Endereço padrão do servidor XML-RPC do PLECS
SERVER_URL = "http://localhost:1080/RPC2"

try:
    plecs_server = xmlrpc.client.ServerProxy(SERVER_URL)
    version_info = plecs_server.plecs.getVersion()
    
    print("\n-------------------------------------------")
    print("✅ Conexão BEM-SUCEDIDA!")
    print(f"   Versão do PLECS detectada: {version_info['version']}")
    print("-------------------------------------------")

except ConnectionRefusedError:
    print("\n-------------------------------------------")
    print("❌ FALHA NA CONEXÃO: Conexão recusada.")
    print("   Verifique se o 'plecs.exe --server' está")
    print("   em execução no Prompt de Comando (CMD).")
    print("-------------------------------------------")
except Exception as e:
    print(f"\n❌ Ocorreu um erro inesperado: {e}")

print("Teste de conexão finalizado.")