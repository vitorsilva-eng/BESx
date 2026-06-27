---
phase: 10
plan: 2
wave: 2
depends_on:
  - plan-1
files_modified:
  - src/besx/application/simulation.py
  - src/besx/infrastructure/ui/streamlit/pages/step_rules.py
  - src/besx/infrastructure/ui/streamlit/pages/step_battery.py
  - src/besx/infrastructure/ui/streamlit/pages/step_results.py
autonomous: true
must_haves:
  truths:
    - "Pipeline de simulação executa os cálculos financeiros ao final e salva no Pickle (.pkl)"
    - "Inputs de tarifas e custos são exibidos e persistidos corretamente nos passos correspondentes"
    - "Painel financeiro do Passo 4 plota gráficos de fluxo de caixa e exibe VPL, TIR, Payback e LCOS corretamente"
  artifacts:
    - "Nova aba '💰 Viabilidade Financeira' funcional no Streamlit"
---

# Plan 10.2: Simulation Integration and Streamlit UI Components

<objective>
Conectar a análise financeira na orquestração do simulador física-degradação e expor as variáveis e resultados gráficos na UI do Streamlit.

Purpose: Disponibilizar a análise financeira ponta a ponta na interface.
Output: Integração de dados em simulation.py e as telas de entrada e saída na UI do Streamlit.
</objective>

<context>
Load for context:
- .gsd/phases/10/01-PLAN.md
- src/besx/application/simulation.py
- src/besx/infrastructure/ui/streamlit/pages/step_rules.py
- src/besx/infrastructure/ui/streamlit/pages/step_battery.py
- src/besx/infrastructure/ui/streamlit/pages/step_results.py
</context>

<tasks>

<task type="auto">
  <name>Integrate Financial Logic in SimulationManager</name>
  <files>src/besx/application/simulation.py</files>
  <action>
    Importar `FinancialAnalyzer` e instanciá-lo ao final da simulação no método `_finalizar_simulacao`.
    Calcular a economia mensal acumulada e projetar o fluxo de caixa com base nos meses simulados.
    Salvar o resumo de fluxo de caixa e os KPIs (VPL, TIR, Payback, LCOS) no arquivo Pickle (.pkl) de resultados e no config_snapshot.json.
    AVOID: Modificar a orquestração de I/O do checklist de checkpoints. Apenas adicione a consolidação no final.
  </action>
  <verify>Verificar se o config_snapshot.json gerado após simular contém chaves como "kpis_financeiros" contendo "lcos".</verify>
  <done>Manager calcula e exporta os dados de retorno financeiro e LCOS.</done>
</task>

<task type="auto">
  <name>Add Tarif and Cost UI Inputs</name>
  <files>
    - src/besx/infrastructure/ui/streamlit/pages/step_rules.py
    - src/besx/infrastructure/ui/streamlit/pages/step_battery.py
  </files>
  <action>
    - Em `step_rules.py` (Passo 1): Criar um bloco colapsável de Tarifas e Reajustes. Incluir inputs para modalidade (Verde/Azul), tarifa de demanda ponta/fora ponta, tarifa de energia ponta/fora ponta, e as taxas anuais de reajuste das tarifas. Persistir no `st.session_state`.
    - Em `step_battery.py` (Passo 2): Adicionar campos de custos (CAPEX R$/kWh instalado, CAPEX Fixo adicional e OPEX de manutenção %). Persistir no `st.session_state.battery_config`.
    AVOID: Perder os estados dos widgets originais. Garantir chaves únicas.
  </action>
  <verify>Executar a UI e validar se as entradas tarifárias e de custos mantêm os valores ao alternar de aba.</verify>
  <done>Inputs integrados e persistidos no Streamlit.</done>
</task>

<task type="checkpoint:human-verify">
  <name>Create Financial Viability UI Tab</name>
  <files>src/besx/infrastructure/ui/streamlit/pages/step_results.py</files>
  <action>
    Criar a nova aba "Viabilidade Financeira" dentro da interface de resultados (`render_dashboard`).
    Calcular as métricas financeiras usando as configurações em cache e renderizar cards para CAPEX Total, VPL, TIR, Paybacks e LCOS (nivelado em R$/kWh).
    Plotar um gráfico Plotly dinâmico para o fluxo de caixa acumulado e anual. Exibir tabela formatada com R$ e porcentagens.
    AVOID: Quebrar o carregamento de resultados legados que não possuem dados financeiros no Pickle. Tratar com fallback seguro ou "N/A".
  </action>
  <verify>Fazer o upload de uma simulação no Passo 4 e verificar se a aba financeira renderiza os gráficos, cartões e o LCOS perfeitamente.</verify>
  <done>Visualização rica integrada (com LCOS) e testada no dashboard.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] Simulação completa grava os dados financeiros em arquivos locais.
- [ ] Streamlit exibe corretamente a aba 💰 Viabilidade Financeira com dados reais do BESS (incluindo o LCOS).
</verification>

<success_criteria>
- [ ] Todo o pipeline financeiro integrado sem erros.
- [ ] A interface Streamlit exibe visualização gráfica de payback, fluxo de caixa e o indicador LCOS de forma interativa.
</success_criteria>
