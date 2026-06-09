import os
import sys

# Força o encoding do stdout para UTF-8 para evitar problemas no terminal Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

steps_config = [
    {"id": "step1", "label": "📋 1. Regras do Local", "status": "ems_injected"},
    {"id": "step2", "label": "🔋 2. Escolha da Bateria", "status": ""},
    {"id": "step3", "label": "⚙️ 3. Simulação Física", "status": "sim_status"},
    {"id": "step4", "label": "📊 4. Resultados", "status": ""},
    {"id": "step5", "label": "📈 5. Comparativo A/B", "status": ""},
    {"id": "step6", "label": "🛠️ 6. Configurações", "status": ""}
]

def test():
    print("=== TESTANDO COMPARAÇÕES DE STRINGS ACENTUADAS ===")
    
    for step in steps_config:
        label = step["label"]
        clean_label = "".join(c for c in label if ord(c) < 65536)  # Remove emojis de alta ordem para segurança do terminal
        
        # Testando Passo 1
        if step["id"] == "step1":
            match = "1. Regras" in label
            print(f"Label: '{clean_label}' | Contém '1. Regras'? {match}")
            
        # Testando Passo 2
        elif step["id"] == "step2":
            match = "2. Escolha" in label
            print(f"Label: '{clean_label}' | Contém '2. Escolha'? {match}")
            
        # Testando Passo 3
        elif step["id"] == "step3":
            match = "3. Simulação" in label
            print(f"Label: '{clean_label}' | Contém '3. Simulação'? {match}")
            
        # Testando Passo 4
        elif step["id"] == "step4":
            match = "4. Resultados" in label
            print(f"Label: '{clean_label}' | Contém '4. Resultados'? {match}")
            
        # Testando Passo 5
        elif step["id"] == "step5":
            match = "5. Comparativo" in label
            print(f"Label: '{clean_label}' | Contém '5. Comparativo'? {match}")
            
        # Testando Passo 6
        elif step["id"] == "step6":
            match = "6. Configurações" in label
            print(f"Label: '{clean_label}' | Contém '6. Configurações'? {match}")

if __name__ == "__main__":
    test()
