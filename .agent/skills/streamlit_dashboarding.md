---
name: Streamlit Dashboarding para BESx
description: Padrões de design e componentes para o dashboard do simulador.
---

# Streamlit Dashboarding no BESx

Diretrizes para manter o dashboard consistente, performático e visualmente premium.

## 1. Identidade Visual

O BESx deve seguir uma estética moderna e científica.

- **Cores Sugeridas:** Azul cobalto, Cinza escuro (Dark Mode) e Verde Esmeralda (para indicadores positivos).
- **Tipografia:** Usar fontes sans-serif limpas (Inter, Roboto).

## 2. Estrutura de Layout

Utilizar a estrutura modular do Streamlit:

- **Sidebar:** Parâmetros de configuração (SoC inicial, Perfil de carga, Tecnologia).
- **Main Area:**
  - `st.columns` para KPIs principais (SOH final, Receita, ROI).
  - `st.tabs` para separar: "Simulação", "Degradação", "Financeiro".

## 3. Visualização de Dados

- **Gráficos:** Priorizar `plotly` ou `altair` para interatividade.
- **Micro-interações:**
  - Usar `st.status` para processos longos (como simulação PLECS).
  - Usar `st.metric` com delta para comparações entre cenários.

## 4. Performance

- **Cache:** Utilizar `@st.cache_data` para carregamento de perfis CSV e `@st.cache_resource` para conexões com o PLECS.
- **Fragmentos:** Usar `st.fragment` para atualizar gráficos sem recarregar a página inteira.

## 5. Exemplo de Componente KPI

```python
def display_kpis(soh_final: float, cycles: int):
    col1, col2 = st.columns(2)
    col1.metric("SOH Final", f"{soh_final:.2%}", delta="-0.5%")
    col2.metric("Ciclos Totais", cycles)
```
