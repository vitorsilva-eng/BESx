# BESx - Simulação de Degradação de Baterias (BESS)

Este projeto realiza a simulação de sistemas de armazenamento de energia em baterias (BESS), integrando modelos de degradação com simulações elétricas via PLECS.

O objetivo principal é avaliar a degradação da bateria (perda de SOH - State of Health) ao longo do tempo, considerando tanto o envelhecimento cíclico (Rainflow) quanto o envelhecimento calendárico.

## Funcionalidades Principais

- **Integração com PLECS**: Comunicação via XML-RPC para executar simulações elétricas.
- **Modelo de Degradação**: Cálculos de dano por ciclo (DOD, SOC médio, Temperatura) e calendário (Tempo, SOC, Temperatura).
- **Gerenciamento de Resultados**:
  - Criação automática de pastas por simulação (`results/sim_YYYYMMDD_HHMMSS/`).
  - Geração de relatórios automáticos (`report.txt`).
  - Salvamento de gráficos e planilhas de debug organizados.
- **Modularidade**: Código estruturado em pacote Python (`besx_app`).

## Estrutura do Projeto

```bash
BESx/
├── besx_app/              # Pacote principal da aplicação
│   ├── core/              # Lógica de simulação e conexão com PLECS
│   ├── models/            # Modelos matemáticos de degradação
│   └── utils/             # Manipulação de dados, plots e arquivos
├── database/              # Pasta para colocar seus arquivos de entrada (.mat, .csv)
├── results/               # Saída das simulações (criado automaticamente)
├── tests/                 # Testes unitários
├── config.py              # Arquivo de configuração central
├── main.py                # Script de execução
└── requirements.txt       # Dependências
```

## Pré-requisitos

1. **Python 3.8+**
2. **PLECS Standalone**: Com o servidor XML-RPC habilitado (padrão na porta 1080).
    - O modelo `bess_batch_mode.plecs` deve estar acessível conforme configurado em `config.py`.

## Instalação

1. Clone este repositório.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como Usar

1. **Configuração**:
    - Ajuste os parâmetros em `config.py` (capacidade, dados de entrada, limites).
    - Coloque seus arquivos de dados na pasta `database/`.

2. **Execução**:
    - Certifique-se que o PLECS está aberto com o servidor XML-RPC ativo.
    - Rode o script:

```bash
python main.py
```

1. **Resultados**:
    - A cada execução, uma nova pasta será criada em `results/` com a data e hora.
    - Verifique `report.txt` para um resumo rápido.
    - Gráficos estarão em `results/.../plots/`.
    - Dados detalhados em `results/.../data/` e `results/.../debug/`.
