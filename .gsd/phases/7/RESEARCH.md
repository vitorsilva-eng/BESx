---
phase: 7
level: 2
researched_at: 2026-05-04
---

# Phase 7 Research: Power Factor Correction

## Questions Investigated
1. O que é necessário para calcular a correção do fator de potência de forma vetorizada no EMS?
2. Como lidar com a prioridade entre Potência Ativa (W) e Reativa (VAr) no inversor?
3. Quais entradas adicionais são necessárias no `EMSManager` e `BessEMS`?
4. Quais são as combinações mínimas de dados de entrada que o EMS deve suportar para realizar as inferências de FP e Reativo?

## Findings

### Matemática Vetorizada
A correção do fator de potência visa injetar/absorver potência reativa ($Q_{bess}$) para que a carga ajustada mantenha um fator de potência alvo ($PF_{target}$).

As fórmulas vetorizadas para Pandas/Numpy são:
1. $S_{max}$ = Capacidade aparente do Inversor (VA).
2. $Q_{alvo} = P_{carga\_ajustada} \times \tan(\arccos(PF_{target}))$
3. $Q_{necessario} = Q_{carga} - Q_{alvo}$
4. A capacidade reativa disponível no inversor é limitada pela potência ativa já despachada (Peak Shaving / Load Shifting):
   $Q_{disponivel} = \sqrt{\max(0, S_{max}^2 - P_{bess}^2)}$
5. O setpoint final de $Q_{bess}$ é o $Q_{necessario}$ limitado pelo $Q_{disponivel}$.

**Recommendation:** Implementar uma nova estratégia `PowerFactorCorrectionStrategy` que será rodada **após** as estratégias de potência ativa, para utilizar o limite de potência aparente sobrante do inversor.

### Inferência e Combinações de Dados de Entrada
Para o EMS calcular a correção do fator de potência, é obrigatório preencher o triângulo de potências da carga. O `EMSManager` deve ser robusto para aceitar qualquer uma das seguintes combinações mínimas:
1. **Ativa (P) e Fator de Potência (FP):**
   - $S = P / FP$
   - $Q = P \times \tan(\arccos(FP))$
2. **Ativa (P) e Reativa (Q):**
   - $S = \sqrt{P^2 + Q^2}$
   - $FP = P / S$
3. **Ativa (P) e Aparente (S):**
   - $Q = \sqrt{S^2 - P^2}$
   - $FP = P / S$
4. **Aparente (S) e Fator de Potência (FP):**
   - $P = S \times FP$
   - $Q = \sqrt{S^2 - P^2}$

**Recommendation:** Atualizar o método `validate_and_prepare_input` do `EMSManager` para identificar as colunas presentes, realizar a inferência utilizando vetorização, e padronizar internamente as colunas `Carga_W`, `Carga_VAr`, `Carga_VA` e `Carga_FP`.

### Alterações na Arquitetura
O EMS atualmente manipula apenas `Potencia_Bateria_W`.
Precisaremos de:
- Expandir a validação para inferir `Load_VAr` (Potência Reativa da Carga) a partir das combinações de dados acima.
- Adicionar `s_inversor_va` (Capacidade do Inversor em VA) no `EMSManager` para conhecer o limite dinâmico de injeção reativa.
- `BessEMS` deve ganhar um método `gerar_perfil_power_factor_correction`.

## Decisions Made
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Prioridade | Ativa depois Reativa | O EMS atual é focado em kW. A correção de fator de potência usará a capacidade de kVA restante (Q_disponivel). |
| Vetorização | Numpy/Pandas Puros | Para manter o `EMSManager` operando em O(1) e ser determinístico. |
| Tratamento de Erros | Falha Graciosa | Se não houver dados de VAr na carga, a estratégia levanta um erro ou não faz nada. |

## Patterns to Follow
- Uso do decorador `@st.cache_data` se envolver Streamlit (mas a implementação do EMS deve ficar pura em `ems_engine.py` e `ems_manager.py`).
- Manter o padrão Pydantic para novos parâmetros de configuração se aplicável.
- Documentar usando numpy/google docstrings, evidenciando as equações de $Q$ e $S$.

## Anti-Patterns to Avoid
- Loops for iterativos: Proibido calcular a correção linha a linha (viola as regras O(1) e vetorização explícita).

## Dependencies Identified
| Package | Version | Purpose |
|---------|---------|---------|
| numpy   | 2.1.3   | Para as funções matemáticas `np.sqrt` e `np.clip`. |

## Risks
- Falta de limites (clip) em raízes quadradas (ex: números negativos se $P_{bess} > S_{max}$ por erro de arredondamento) resultando em NaNs.
- **Mitigação:** Usar `np.clip(S_max**2 - P_bess**2, a_min=0, a_max=None)` antes do `np.sqrt`.

## Ready for Planning
- [x] Questions answered
- [x] Approach selected
- [x] Dependencies identified
