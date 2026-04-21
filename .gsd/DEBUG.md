# Debug Session: NameError in step_settings.py

## Symptom

`NameError: name 'PERFIS_BATERIA' is not defined` quando a suite de validação é executada.

**Quando:** 2026-04-07 10:22:24 (Reportado pelo usuário)

**Esperado:** A função de validação `rodar_validacao` deve receber o nome do perfil de bateria padrão.

**Atual:** O aplicativo falha porque `PERFIS_BATERIA` não está no escopo de `render_step_settings`.

## Evidence

- `src/besx/infrastructure/ui/streamlit/pages/step_settings.py` linha 73: `perfil_atual = list(PERFIS_BATERIA.keys())[0]`
- Imports em `step_settings.py`: `from besx.config import CONFIGURACAO, ModeloDegradacaoConfig` (Faltava `PERFIS_BATERIA`)

## Hypotheses

| # | Hypothesis | Likelihood | Status |
|---|------------|------------|--------|
| 1 | `PERFIS_BATERIA` faltando nos imports em `step_settings.py` | 100% | CONFIRMED |

## Attempts

### Attempt 1

**Testing:** H1 — Adição de `PERFIS_BATERIA` aos imports.

**Action:** Atualizamos `src/besx/infrastructure/ui/streamlit/pages/step_settings.py`.

**Result:** PASS

**Conclusion:** CONFIRMED

## Resolution

**Root Cause:** Import ausente da constante `PERFIS_BATERIA` no arquivo da interface de configurações.

**Fix:** Adicionado `PERFIS_BATERIA` à lista de imports de `besx.config` no arquivo `step_settings.py`.

**Verified:** Verificado via análise de código e correção direta conforme stack trace.

## Regression Check: Verificado que outros arquivos (`step_battery.py`, `step_simulation.py`) já importavam a constante corretamente.

---

# Debug Session: PLECS Validation Failure on Streamlit

## Symptom

`Não foi possível carregar os dados de cross-validation. O PLECS pode estar fechado ou o perfil falhou.` quando a validação cruzada do PLECS (TC4) é ativada via Streamlit.
Porém, `plecs_connector.py` em simulação temporal (e a execução pelo shell local) rodam o motor PLECS normalmente! O XML-RPC está de pé, e o PLECS Scope está exportando.

**Quando:** 2026-04-07 10:53:04 (Reportado pelo usuário)
**Esperado:** A UI deve desenhar os 3 gráficos Plotly referentes a (TC4) Cross-Validation comparando Python e o motor PLECS.
**Atual:** Cai no bloco de erro customizado do `step_settings.py` porque `cross_data['plecs']` foi retornado como `None`.

## Evidence
- Execução rodando Python em CLI (`import test_engine_validation` e chamando `rodar_validacao`) rodou perfeitamente e exportou as métricas. Nenhuma exceção no connector.
- Simulação Temporal também funciona perfeitamente dentro do Streamlit.
- O bloqueio está atrelado EXCLUSIVAMENTE ao acionamento do TC4 **via Streamlit**.
- O script `plecs_connector.py` suprime erros (`return None`) na criação do `.mat`, comunicação `xmlrpc`, e parse do `/dadosnovos.csv`. Como o Streamlit abafa os logs do bash dentro da sua Virtual Thread, não conseguimos ver onde a exceção ocorre.

## Hypotheses

| # | Hypothesis | Likelihood | Status |
|---|------------|------------|--------|
| 1 | Erro de Path do DataFrame: Em Streamlit a pasta raiz (CWD) altera a leitura do `/dadosnovos.csv` para algo como `pages/dadosnovos.csv`. | 60% | UNTESTED |
| 2 | Oplecs do Streamlit tenta ler um arquivo antes do PLECS terminar de salvar o CSV por latência temporal. | 30% | UNTESTED |
| 3 | O backend PLECS bloqueia a segunda instância do XML-RPC dentro de Threads do Streamlit. | 10% | UNTESTED |

## Attempts

### Attempt 1
**Testing:** H1 — Identificar o Silent Error
**Action:** Injetamos rastreadores temporários de Erro (`.gsd/last_plecs_error.log`) nos blocos `try/except` omitidos de `plecs_connector.py` e `test_engine_validation.py`.
**Conclusion:** UNTESTED (Aguardando o usuário clicar no botão e gerar o novo disparo de erro).
