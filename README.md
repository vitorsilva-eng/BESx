# 🔋 BESx - Battery Energy Storage Simulator

O **BESx** é um simulador avançado de sistemas de armazenamento de energia em baterias (BESS), focado em modelagem de degradação baseada na física (Physics-Informed) e teoria de fadiga. O projeto é estruturado em uma arquitetura limpa, separando o motor de simulação (Core) da interface visual interativa (Dashboards).

---

## 🎯 Visão Geral e Capacidades

- **Simulação Científica Precisa:** Utiliza o *Modelo Empírico de Stroe* e o algoritmo de *Rainflow Cycle Counting* para extrair microciclos (DOD e SOC Médio) e calcular os danos cumulativos da bateria com precisão rigorosa.
- **Acumulação Não-Linear Estrita:** A degradação (cíclica e calendárica) obedece estritamente a regras de potência e modelos geométricos, descartando somas lineares irreais (Miner-Stroe rules).
- **Extensibilidade Híbrida (PIML):** Arquitetura desenhada estruturalmente para integração contínua com camadas de Aprendizado de Máquina (Physics-Informed Machine Learning), operando sobre a modelagem de resíduos.
- **Monitoramento e Validação Contínua:** Módulo visual especializado (Engine Validation) para atestar em tempo real o funcionamento comparativo das regras físicas durante transientes de energia.

---

## 🏗️ Estrutura e Arquitetura do Projeto

O projeto segue os princípios de separação de responsabilidade, garantindo que as lógicas pesadas O(n) não contaminem a reatividade da interface.

- `src/besx/domain/`: Lógica central, equações diferenciais, motor empírico de simulação e contagem iterativa de fadiga.
- `src/besx/entrypoints/`: Estruturação das duas vias independentes de acesso:
  - `cli/`: Interface de linha de comando para simulações Headless seguras.
  - `dashboard/`: A interface do **Streamlit** (arquitetura reativa, com state management forte usando `st.session_state` e `@st.cache_data`).
- `database/`: Armazenamento padronizado de referências de catálogos e parâmetros eletroquímicos nominais.
- `data/` & `results/`: Dutos de I/O para injeção de perfis de energia (telemetria) e consolidação analítica.

---

## 🚀 Guia de Execução (Getting Started)

### 1. Requisitos do Sistema
- **Python 3.11+**
- Gerenciador de dependências configurado (instalação stricta com as bibliotecas marcadas no `pyproject.toml` para garantir durabilidade e evitar "Environment Smells").

### 2. Iniciando o Dashboard de Visualização
O ambiente visual pode ser inicializado utilizando o utilitário configurado:
```bash
./run_dashboard.bat
```

### 3. Iniciando Modo CLI (Batch / Terminal)
Para executar rastreios analíticos puros sem a sobrecarga das bibliotecas de renderização, utilize a interface de linha de comando:
```bash
./run_cli.bat
```

---

## 🛠️ Diretrizes Rigorosas de Desenvolvimento

Toda colaboração e alteração no repositório **devem** obedecer aos padrões internos descritos abaixo (e detalhados em `besx-standards.md`):

1. **Tipagem Estática (Type Hints):** 100% obritagório em novas assinaturas.
2. **Documentação Acadêmica:** Funções de cálculo base devem apresentar Docstrings no formato Google ou NumPy formatado com as deduções paramétricas.
3. **Observabilidade (No Prints):** Proibido o uso de `print()`. Utilizar os singletons predefinidos em `besx_app.utils.logger`.
4. **Pydantic Native:** Estruturas complexas (Dutos de Dados e Configurações) devem ser modeladas usando Pydantic, impedindo a injeção falha por dicionários cegos.
5. **Independência de Trajetos (OS Pathing):** Abolição definitiva de caminhos duros inter-drives do sistema. As rotas devem ser deduzidas internamente em tempo de construção.

---

## 📜 Licença e Referências
*Property of BESx Team.*
Consulte os administradores de núcleo (Lead Software Engineering e Core Data Science) para requisição de Merge Requests e discussões arquiteturais.
