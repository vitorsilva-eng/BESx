# DECISIONS.md

## Log
| Date | Decision | Rationale | Status |
|------|----------|-----------|--------|
| 2026-03-12 | SD-001 (Persistence via .csv Exchange) | User selected Option B. Profile will be saved to disk for better reproducibility and external debugging. | APPROVED |
## Phase 8 Decisions

**Date:** 2026-05-04

### Scope
- Implementação visual da estratégia de Power Factor Correction (PFC) no dashboard.
- PFC será tratado como uma estratégia exclusiva no seletor de algoritmos (por enquanto).
- Visualização de reativos e FP será isolada em uma nova aba de "Qualidade".

### Approach
- **Inputs**: Adicionado ao radio button de algoritmos principais no Passo 1.
- **S_max**: A capacidade do inversor (VA) será vinculada ao cadastro do BESS/Inversor no Passo 2, mas para o preview do EMS, utilizaremos um valor padrão vindo da configuração.
- **Charts**: Utilização de plots dedicados para VAr (Original vs Ajustado) e FP (Original vs Ajustado).

### Constraints
- Inferência de triângulo de potências assume FP=1.0 se colunas elétricas estiverem ausentes no CSV.

## Phase 10 Decisions

**Date:** 2026-06-27

### Scope
- **Projeção e Degradação**: Será adotada a Opção A, ou seja, a projeção financeira cobrirá estritamente o prazo simulado fisicamente pelo usuário, permitindo o acoplamento exato da degradação (SOH) calculada pelo motor.
- **Estrutura Tarifária**: Desconsiderar bandeiras tarifárias e assumir que as tarifas inseridas pelo usuário já contêm todos os impostos.
- **Multa por Reativos Excedentes**: A engine financeira calculará ativamente a multa por reativo excedente (faturamento com base em FP < 0.92, conforme regulação da ANEEL) e contabilizará a economia correspondente quando a estratégia de PFC estiver ativa.
- **Depreciação e OPEX**:
  - **Depreciação**: Taxa linear padrão de **10% ao ano** sobre o CAPEX inicial (vida útil de 10 anos).
  - **Manutenção (OPEX)**: Custo anual padrão de **1.5% do CAPEX inicial** ao ano, reajustado pela inflação.

### Approach
- **Custos do BESS (CAPEX/OPEX)**: Inseridos na interface do Passo 2 (Hardware).
- **Tarifas (Demanda e Energia)**: Inseridos na interface do Passo 1 (Regras do Local).
- **Resultados**: Apresentados em uma nova aba "💰 Viabilidade Financeira" no Passo 4 (Resultados), exibindo o fluxo de caixa anual estruturado e os indicadores VPL, TIR e Paybacks.
- **Validação de TIR**: O indicador exibirá "TIR: N/A (Sem Retorno Real)" caso o cálculo matemático de Newton-Raphson/Secante não convirja, protegendo a UI de falhas.
