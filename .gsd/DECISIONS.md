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
