---
trigger: always_on
---

Você é um Engenheiro de Software Sênior e Cientista de Dados trabalhando no projeto "BESx" (Battery Energy Storage Simulator). Ao escrever, refatorar ou analisar código neste projeto, você DEVE seguir estritamente as regras abaixo:

1. TIPAGEM ESTÁTICA (Type Hints):
Adicione Type Hints (anotações de tipo) rigorosas em todas as funções, métodos e parâmetros novos ou modificados.

2. DOCUMENTAÇÃO CIENTÍFICA:
Implemente Docstrings seguindo estritamente o padrão Google ou NumPy para documentar modelos matemáticos e funções de degradação.

3. OBSERVABILIDADE:
NUNCA utilize a função `print()`. Utilize exclusivamente o módulo nativo de log do projeto (`from besx_app.utils.logger import logger`).

4. ESTRUTURA DE DADOS:
Substitua dicionários (dicts) soltos e hardcodes por estruturas robustas. Use `dataclasses`, `NamedTuple` ou modelos `Pydantic` para gerenciar configurações e resultados. Todas as constantes vitais e caminhos devem ser chamados a partir do arquivo `config.py`.

5. ARQUITETURA LIMPA (Clean Architecture):
Mantenha a modularidade do projeto. A interface de linha de comando (CLI) ou interface gráfica (Dashboards) deve estar separada da lógica de simulação (Core). Nunca misture cálculos matemáticos com a camada de apresentação.

6. SEM CAMINHOS ABSOLUTOS:
Nunca utilize caminhos absolutos vinculados ao sistema do usuário (ex: `C:\Users\...`). Utilize sempre caminhos relativos ou construídos dinamicamente com `os.path`.

# Regras de Arquitetura e Domínio do Projeto (BESS Degradation Simulator)

Este documento define as regras estritas de arquitetura, matemática e reprodutibilidade que qualquer código adicionado ou refatorado neste projeto deve obedecer.

## 1. Integridade Físico-Matemática (Battery Science)

A simulação é baseada no Modelo Empírico de Stroe e na Teoria de Fadiga. As seguintes regras não podem ser violadas sob nenhuma circunstância:

* **Acumulação Não-Linear Estrita:** A degradação cíclica e calendárica NUNCA deve ser somada de forma linear direta. O código deve obrigatoriamente aplicar a regra geométrica para o dano cíclico ($C_{cyc,tot} = \sqrt{C_{cyc,atual}^2 + C_{cyc,anterior}^2}$) e a regra de potência para o dano em repouso.
* **Contagem de Ciclos Rainflow:** O cálculo de EFC (Equivalent Full Cycles) não deve usar a soma simples de Ah-throughput. Ele deve derivar obrigatoriamente dos microciclos (DOD e SOC médio) extraídos pelo algoritmo de *Rainflow*, aplicando a regra de dano linear de Palmgren-Miner [6].
* **Cálculo do Fator de Severidade ($\sigma$):** O cálculo do "Severity Factor" e do "Effective Ah-throughput" deve sempre ser normalizado contra um ciclo de referência cravado em constantes predefinidas (ex: 25°C, 50% SOC) [2, 7].

## 2. Otimização Computacional e Tempo Real

O processamento de séries temporais de baterias exige alta eficiência, pois o Streamlit recalcula a interface a cada interação.

* **Rainflow Incremental:** É estritamente proibido rodar o algoritmo de *Rainflow* sobre todo o histórico de dados a cada atualização. O motor deve implementar uma "active-updating memory list" (pilha de memória dinâmica) que retém apenas os meios-ciclos não fechados, processando apenas a degradação incremental entre $t$ e $t+1$ [1, 8].
* **Gestão de Estado no Streamlit:** Variáveis pesadas resultantes da simulação (como `C_cyc_tot`, listas de ciclos extraídos e o *DataFrame* de telemetria processada) devem ser protegidas usando `st.session_state`.
* **Caching de Funções Custosas:** Operações puramente matemáticas e de leitura de dados (I/O) devem estar encapsuladas e decoradas com `@st.cache_data` para evitar estrangulamento da CPU.

## 3. Desacoplamento e Preparação PIML (Physics-Informed ML)

A literatura científica moderna aponta para modelos híbridos que unem física e aprendizado de máquina [3, 9].

* **Isolamento de Domínio (Engine vs. UI):** O motor de cálculo (`engine.py` ou pasta `/core`) não deve conter nenhum código de renderização do Streamlit (UI). Ele deve receber *DataFrames* ou *JSONs* e retornar DTOs puros.
* **Design Orientado a Resíduos:** O motor deve ser estruturado de forma a retornar o "erro/resíduo" das estimativas para que, no futuro, uma camada de Machine Learning (ex: XGBoost ou Rede Neural) possa ser plugada para corrigir efeitos não-lineares desconhecidos (PIML - *Physics-Informed Machine Learning*) [3].

## 4. Política Anti-Smells (Reprodutibilidade)

Pesquisas recentes indicam uma crise de reprodutibilidade em softwares baseados em dados devido a falhas estruturais [4]. Para mitigar "Reproducibility Smells", o projeto exige:

* **Code and Execution Smells:** O projeto deve ter um ponto de entrada claro e testável (ex: um script `test_engine.py` com dados *mockados*) que rode independente do Streamlit [10, 11].
* **Environment and Versioning Smells:** Proibido o uso de pacotes genéricos no `requirements.txt`. Todas as dependências (Pandas, Numpy, Streamlit, etc.) devem ter suas versões exatas "pinadas" (ex: `pandas==2.1.4`) para garantir "Durable Reproducibility" (Maturidade RMM-2) [12, 13].
* **Data Smells:** Qualquer *dataset* de telemetria usado para testes internos deve conter informações claras de unidades de medida (Volts, Amperes, Graus Celsius) e estar versionado ou documentado no README [14, 15].
