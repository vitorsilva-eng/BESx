---
phase: 10
plan: 1
wave: 1
depends_on: []
files_modified:
  - src/besx/config.py
  - src/besx/application/analysis/financial_analyzer.py
  - tests/test_financial.py
autonomous: true
must_haves:
  truths:
    - "Modelos Pydantic contêm parâmetros financeiros no config"
    - "Cálculos de VPL, TIR e Payback funcionam corretamente sem dependências externas"
    - "Cálculo de faturamento do Grupo A e multa de reativo validado"
  artifacts:
    - "src/besx/application/analysis/financial_analyzer.py existe"
    - "tests/test_financial.py existe"
---

# Plan 10.1: Configuration and Core Financial Engine

<objective>
Configurar as variáveis de faturamento e custos no Pydantic global e desenvolver a engine de cálculos financeiros robusta e testada.

Purpose: Estabelecer as bases matemáticas e estruturais da análise financeira.
Output: Alterações de configuração, a classe `FinancialAnalyzer` e cobertura de testes.
</objective>

<context>
Load for context:
- .gsd/ROADMAP.md
- .gsd/DECISIONS.md
- src/besx/config.py
</context>

<tasks>

<task type="auto">
  <name>Implement FinancialConfig in config.py</name>
  <files>src/besx/config.py</files>
  <action>
    Criar a classe Pydantic `FinancialConfig` contendo capex_por_kwh, capex_fixo_implementacao, opex_manutencao_anual_perc, taxa_desconto_wacc, reajuste_tarifario_anual_perc, reajuste_opex_anual_perc, modalidade_tarifaria, tarifas de energia e tarifas de demanda.
    Acoplá-la à classe global `Settings` para validação e valores padrão seguros.
    AVOID: Alterar o comportamento existente dos perfis de bateria físicos em config.py.
  </action>
  <verify>python -c "from besx.config import CONFIGURACAO; print(CONFIGURACAO.financial)"</verify>
  <done>Classe Pydantic validada e incorporada nas Settings globais.</done>
</task>

<task type="auto">
  <name>Create FinancialAnalyzer Application Class</name>
  <files>src/besx/application/analysis/financial_analyzer.py</files>
  <action>
    Implementar a classe `FinancialAnalyzer` que calcula as faturas sem BESS (Referência) e com BESS (Real).
    Calcular a multa de reativos excedentes se FP < 0.92 (conforme ANEEL).
    Projetar o fluxo de caixa anual descontado aplicando OPEX de manutenção (1.5% do CAPEX inicial, reajustado), Depreciação (10% ao ano linear) e calculando VPL, TIR (via Newton-Raphson com fallback e tratamento para N/A) e Paybacks.
    AVOID: Importar bibliotecas como numpy_financial que violam a stack limpa. Usar a implementação nativa testada.
  </action>
  <verify>pytest tests/test_financial.py</verify>
  <done>Engine de cálculo finalizada com cobertura total de fórmulas.</done>
</task>

<task type="auto">
  <name>Write Core Financial Unit Tests</name>
  <files>tests/test_financial.py</files>
  <action>
    Escrever testes unitários rigorosos para a classe `FinancialAnalyzer` cobrindo o cálculo de faturas Azul/Verde, economia de reativos, cálculo de TIR (casos normais e casos sem convergência que geram "N/A"), VPL e Paybacks.
    AVOID: Mockagem incompleta de perfis de telemetria. Usar dados gerados programaticamente.
  </action>
  <verify>pytest tests/test_financial.py</verify>
  <done>Testes criados e passando com 100% de sucesso.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] Classe `FinancialConfig` acessível via `CONFIGURACAO`.
- [ ] Testes do `FinancialAnalyzer` passando verde.
</verification>

<success_criteria>
- [ ] Todos os testes passando com sucesso.
- [ ] Estrutura matemática validada e isolada da UI.
</success_criteria>
