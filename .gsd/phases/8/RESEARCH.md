---
phase: 8
level: 2
researched_at: 2026-05-04
---

# Phase 8 Research: PFC UI Integration

## Questions Investigated
1. Onde posicionar os controles de PFC no Dashboard para manter a fluidez da UI?
2. Como visualizar o despacho reativo e a melhoria do Fator de Potência de forma intuitiva?
3. Como integrar a nova estratégia no fluxo de execução atual (`step_rules.py`)?
4. Quais colunas adicionais devem ser expostas no diagnóstico de carga?

## Findings

### 1. UI Placement (Inputs)
Os controles de PFC devem residir na subseção "🎯 Estratégia de Despacho" do Passo 1. 
- **Decisão**: Transformar a seleção de estratégia em algo que permita a coexistência do PFC com estratégias de potência ativa (Peak Shaving / Load Shifting), embora inicialmente o motor opere em modo isolado conforme solicitado pelo usuário.
- **Componentes**: 
    - `st.checkbox("Habilitar Correção de Fator de Potência")`
    - `st.number_input("Fator de Potência Alvo", value=0.98, min_value=0.8, max_value=1.0)`
    - `st.number_input("Capacidade do Inversor (kVA)", value=S_MAX_DEFAULT)`

### 2. Visualization (Outputs)
O despacho de reativos (VAr) e o impacto no FP são métricas de "Qualidade de Energia", distintas do fluxo de "Energia/Potência Ativa".
- **Recomendação**: Adicionar uma nova Tab no diagnóstico: `⚡ Qualidade (PFC)`.
- **Gráficos Necessários**:
    - **Gráfico de Potência Reativa**: Comparativo entre `Carga_VAr` (Original) vs `Carga_Ajustada_VAr` (após intervenção da bateria).
    - **Gráfico de Fator de Potência**: Comparativo entre `Carga_FP` vs `Carga_Ajustada_FP`, com linha de referência em 0.92 (limite regulatório).

### 3. Integration Logic
O arquivo `step_rules.py` gerencia a instância do `EMSManager`. 
- **Ação**: No callback do botão "Gerar Preview", se o PFC estiver habilitado, injetar a `PowerFactorCorrectionStrategy` na lista de estratégias do manager.
- **Passagem de Parâmetros**: Utilizar o dicionário `kwargs` já existente para passar `pf_target` e `s_max_va` para o método `run`.

## Decisions Made
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Localização dos Inputs | Estratégia de Despacho (Sidebar/Main) | Mantém todos os parâmetros operacionais em um único lugar. |
| Estrutura de Abas | Nova Aba "Qualidade" | Evita poluir o gráfico de potência ativa (W) com escalas de reativos (VAr). |
| Modo de Operação | Checkbox Adicional | Permite ligar/desligar o PFC de forma independente das outras heurísticas. |

## Patterns to Follow
- **Vetorização**: Continuar usando exclusivamente operações de array do NumPy para cálculos de reativos no motor.
- **Session State**: Armazenar os novos parâmetros (`pf_target`, `s_inversor_va`) no `st.session_state` para persistência entre tabs.

## Anti-Patterns to Avoid
- **Escalas Misturadas**: Não plotar W e VAr no mesmo eixo Y sem escalas secundárias (pode confundir o usuário devido às magnitudes).
- **Recálculo Excessivo**: Garantir que a inferência do triângulo de potências ocorra apenas uma vez durante a validação do input.

## Dependencies Identified
| Package | Version | Purpose |
|---------|---------|---------|
| Plotly | 5.18.0 | Renderização dos novos gráficos de qualidade de energia. |
| NumPy | 1.26.2 | Cálculos trigonométricos (arccos, tan) para inferência de reativos. |

## Risks
- **Dados de Input Incompletos**: Se o usuário subir um CSV apenas com `Potencia_W`, o PFC assumirá `VAr=0` (FP=1.0) a menos que a inferência funcione.
- **Mitigação**: O `EMSManager` já possui lógica de inferência para preencher `Carga_VAr` com 0 caso não exista, o que é seguro (não há o que corrigir).

## Ready for Planning
- [x] Questions answered
- [x] Approach selected
- [x] Dependencies identified
