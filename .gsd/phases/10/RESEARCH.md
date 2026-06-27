---
phase: 10
level: 2
researched_at: 2026-06-27
---

# Phase 10 Research: Financial Analysis

## Questions Investigated
1. Como modelar as tarifas de energia e demanda no Brasil para o Grupo A (tarifas Verde e Azul)?
2. Como calcular os custos de aquisição (CAPEX), operacionais (OPEX) e reinvestimento (RE-CAPEX) para projetos BESS?
3. Como estruturar a modelagem financeira de fluxo de caixa levando em conta a degradação física da bateria ao longo dos anos?
4. Como calcular indicadores de viabilidade financeira (VPL, TIR, Payback Simples e Descontado) de forma isolada, sem adicionar dependências externas complexas?
5. Como calcular e integrar o LCOS (Levelized Cost of Storage) na análise do ciclo de vida útil do BESS?
6. Onde e como a análise financeira deve ser integrada na arquitetura limpa do projeto (Core, SimulationManager e Streamlit UI)?

## Findings

### 1. Tarifação Horo-Sazonal (Grupo A) no Brasil
Consumidores comerciais e industriais (Grupo A) são faturados sob as seguintes modalidades:
- **Tarifa Verde**:
  - Demanda única contratada faturada em R$/kW (independente do posto).
  - Consumo de energia em R$/kWh diferenciado por posto (Ponta e Fora de Ponta).
- **Tarifa Azul**:
  - Demanda contratada diferenciada por posto (Ponta e Fora de Ponta) em R$/kW.
  - Consumo de energia em R$/kWh diferenciado por posto (Ponta e Fora de Ponta).
- **Ultrapassagem de Demanda**: Caso a demanda medida em algum posto supere 105% da contratada, cobra-se uma multa de ultrapassagem calculada como:
  \[ C_{ultrapassagem} = (D_{max} - D_{contratada}) \times T_{demanda} \times 2 \]
  O algoritmo de Peak Shaving do BESS atua diretamente reduzindo a demanda medida, gerando economia dupla: redução da demanda faturada e eliminação da multa de ultrapassagem.

### 2. Custos de BESS (CAPEX & OPEX)
- **CAPEX (Investimento Inicial)**: Calculado a partir da capacidade nominal total do BESS em kWh. Valores típicos de mercado no Brasil variam de R$ 1.100 a R$ 1.500 por kWh instalado. É recomendável adicionar um CAPEX fixo de implementação (obra civil, engenharia, frete).
- **OPEX (Custo Operacional)**: Estimado como um percentual fixo anual do CAPEX (ex: 0,5% a 1,0% ao ano) ou valor fixo anual em R$, reajustado pela inflação.
- **RE-CAPEX (Reinvestimento)**: Custos de reposição de inversores ou outros componentes previstos no ano 10 (ex: 15% do CAPEX inicial).

### 3. Integração Matemática: Física + Finanças (Degradação)
- A simulação de longo prazo fornece a perda progressiva da bateria (SOH caindo). 
- Conforme o SOH diminui, a capacidade da bateria diminui. Isso limita o throughput mensal da bateria para arbitragem e a potência disponível para Peak Shaving.
- O motor de simulação (`SimulationManager`) já roda a telemetria degradada mensalmente. Ao acumular a economia gerada pela simulação mês a mês ao longo dos anos, os benefícios financeiros decrescem naturalmente com a degradação real da bateria. Isso cria um modelo financeiro "Physics-Informed", muito mais realista que os modelos de mercado baseados em planilhas que supõem economia constante.

### 4. Indicadores Financeiros
Implementação robusta em Python puro (Newton-Raphson e método da secante para TIR) evitando dependências externas como `numpy_financial`.
- **VPL**: Desconto anual dos fluxos pelo WACC.
- **TIR**: Taxa que zera o VPL.
- **Payback Simples e Descontado**: Ponto onde a soma acumulada de fluxos cruza o zero (calculado com interpolação linear para frações de ano).

### 5. Levelized Cost of Storage (LCOS)
O LCOS é uma métrica que expressa o custo médio nivelado para armazenar e entregar cada unidade de eletricidade (R$/kWh ou R$/MWh) ao longo do ciclo de vida do sistema:

\[ \text{LCOS} = \frac{\text{CAPEX} + \sum_{t=1}^{N} \frac{\text{OPEX}_t + \text{Charging Cost}_t + \text{RE-CAPEX}_t}{(1 + WACC)^t}}{\sum_{t=1}^{N} \frac{\text{Electricity Discharged}_t}{(1 + WACC)^t}} \]

- **Charging Cost (Custo de Carregamento):** O custo financeiro associado ao consumo de energia da rede para carregar a bateria. O cálculo considerará a energia real consumida para recarga multiplicada pela tarifa fora de ponta em cada ano. Esse custo é naturalmente ajustado pela eficiência real do sistema de armazenamento (Round-Trip Efficiency) simulado.
- **Electricity Discharged (Eletricidade Descarregada):** A quantidade total de energia ativa fornecida pelo BESS para a carga a cada ano (kWh), decrescendo conforme a degradação da bateria.

### 6. Integração na Arquitetura Limpa
- **Configuração (`src/besx/config.py`)**: Criar a classe Pydantic `FinancialConfig` contendo CAPEX, OPEX, tarifas (Verde/Azul, energia e demanda ponta/fora ponta), reajustes e WACC. Integrá-la à classe global `Settings`.
- **Core de Análise (`src/besx/application/analysis/financial_analyzer.py`)**: Criar uma classe `FinancialAnalyzer` para calcular a fatura de energia sem o BESS (Cenário de Referência) e com o BESS (Cenário Real), projetando o fluxo de caixa anual e calculando os indicadores, incluindo o LCOS.
- **Visualização (`src/besx/infrastructure/ui/streamlit/pages/step_results.py`)**: Adicionar a aba "Viabilidade Financeira" ao Passo 4 para apresentar o fluxo de caixa, KPIs de viabilidade e o LCOS calculado.

## Decisions Made
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Método de Cálculo da TIR | Algoritmo Customizado (Newton-Raphson + Secante) | Evita adicionar a biblioteca `numpy_financial`, mantendo a stack limpa e reduzindo o risco de conflito de versões. |
| Inserção de Dados Tarifários | Sidebar do Passo 1 (Regras do Local) | As tarifas dependem do local da instalação e da modalidade de fornecimento de energia do cliente. |
| Inserção de Dados de Custos | Sidebar do Passo 2 (Hardware) | CAPEX e OPEX dependem diretamente do hardware e capacidade da bateria selecionada. |
| Modelo de Fluxo de Caixa | Physics-Informed | A economia de cada ano será baseada nos meses simulados, que já contêm a degradação de capacidade (SOH), refletindo fielmente a queda de benefício financeiro. |
| Cálculo de LCOS | Nivelamento Descontado por WACC | O WACC deve descontar tanto os fluxos de caixa de custo quanto os volumes de energia descarregada anuais para refletir o custo financeiro do tempo e do capital. |

## Patterns to Follow
- Uso rigoroso de Type Hints e dataclasses/modelos Pydantic.
- Nenhuma chamada direta de cálculo financeiro nas telas (separação de lógica em `financial_analyzer.py`).
- Uso do logger centralizado do projeto (`from besx.infrastructure.logging.logger import logger`).

## Anti-Patterns to Avoid
- Uso de `print()` para logs em produção.
- Hardcode de tarifas no código da UI.
- Linearização simplória da economia anual ignorando a degradação de capacidade da bateria.
- Exclusão do custo de carregamento do cálculo do LCOS.

## Dependencies Identified
Nenhuma nova dependência identificada. Utilizaremos as bibliotecas já existentes (`numpy`, `pandas`, `pydantic`).

## Risks
- **Divergência na Convengência da TIR**: O fluxo de caixa de projetos BESS com OPEX alto ou degradação acelerada pode ter múltiplas taxas de retorno ou nenhuma.
  - *Mitigação*: O algoritmo implementará uma verificação de consistência e fará fallback para o método da secante ou sinalizará erro caso não haja retorno real.

## Ready for Planning
- [x] Questions answered
- [x] Approach selected
- [x] Dependencies identified
