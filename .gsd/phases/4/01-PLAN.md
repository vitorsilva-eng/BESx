---
phase: 4
plan: 1
wave: 1
depends_on: []
files_modified: ["src/besx/infrastructure/ui/streamlit/pages/step_comparison.py"]
autonomous: true
user_setup: []

must_haves:
  truths:
    - "Tabela de comparação apresenta Eficiência Round-trip e DOD Médio"
    - "Gráfico de barras compara Energia de Carga e Descarga"
    - "Histograma de DOD exibe a distribuição de ciclos extraídos pelo Rainflow"
  artifacts:
    - "src/besx/infrastructure/ui/streamlit/pages/step_comparison.py modificado"
---

# Plan 4.1: Enhanced Comparison Dashboard

<objective>
Atualizar a página de comparação para incluir métricas de energia, eficiência e distribuição de DOD, organizando a visualização em abas.
</objective>

<context>
Load for context:
- src/besx/infrastructure/ui/streamlit/pages/step_comparison.py
- src/besx/domain/models/degradation_model.py (EstatisticasOperacionais)
</context>

<tasks>

<task type="auto">
  <name>Expandir Tabela de Métricas</name>
  <files>src/besx/infrastructure/ui/streamlit/pages/step_comparison.py</files>
  <action>
    Atualizar o dicionário `LABELS` e a função `render_diff_table` para incluir:
    - DOD_Medio_Perc (DOD Médio)
    - Energia_Carga_kWh (Energia In)
    - Energia_Descarga_kWh (Energia Out)
    - Eficiência RTE (Calculada na hora)
    - C_Rate_Max (Stress de Corrente)
  </action>
  <verify>Rodar o dashboard e verificar novas linhas na tabela.</verify>
  <done>Novas métricas aparecem corretamente na tabela de diff.</done>
</task>

<task type="auto">
  <name>Implementar Visualizações de Gráficos e Tabs</name>
  <files>src/besx/infrastructure/ui/streamlit/pages/step_comparison.py</files>
  <action>
    - Adicionar `st.tabs(["Visão Geral", "Energia & Eficiência", "Distribuição de Ciclos (DOD)"])`.
    - Mover gráficos de SOH e Dano para a primeira aba.
    - Criar gráfico de barras de energia na segunda aba.
    - Criar histograma de DOD na terceira aba usando `Rainflow_Cycles`.
  </action>
  <verify>Verificar se as abas carregam e se os gráficos Plotly renderizam dados das simulações selecionadas.</verify>
  <done>Gráficos de Energia e Histograma de DOD funcionais e navegáveis via abas.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] Tabela comparativa com métricas de energia e DOD.
- [ ] Gráfico de energia In/Out comparando cenários.
- [ ] Histograma de DOD agregando ciclos de todos os meses da simulação.
</verification>

<success_criteria>
- [ ] Simulações podem ser comparadas em termos de eficiência e estresse operacional além do SOH.
</success_criteria>
