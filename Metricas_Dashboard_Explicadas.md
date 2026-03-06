# Relatório Técnico: Métricas do Gêmeo Digital BESx (Tab 1)

Este documento detalha o significado físico e matemático de cada métrica apresentada na Tab 1 ("Visão Geral" / "Tempo Real") do Dashboard do simulador BESx, incluindo as discrepâncias esperadas em sistemas baseados em contagem de fadiga.

---

## 1. SOH (State of Health)
* **O que é:** Representa a capacidade de armazenamento restante da bateria em relação à sua capacidade original de fábrica. O limite de fim de vida útil (EOL - End of Life) usualmente é fixado em 80%.
* **Como é calculado:** Obtido de forma contínua pelo `SimulationManager`. Ao longo da simulação, os danos de calendário e ciclo reduzem este fator progressivamente.

## 2. Severidade (Is)
* **O que é:** O Fator de Severidade indica quão agressivo tem sido o uso da bateria em proporção a um cenário nominal e empírico de laboratório. 
    * `Is = 1.0`: Desgaste idêntico ao nominal.
    * `Is > 1.0`: Uso agressivo (temperatura elevada, ciclos muito profundos ou permanência em SOC extremo).
* **Como é calculado:** Baseia-se no modelo de referência de *Serrão et al.* A função `calcular_fator_severidade` interna compara o dano real sofrido no mês com o "Dano de Referência" pré-calculado para uma bateria mantida a 25°C, ciclando 30 vezes ao mês em um DOD de 10% com SOC médio de 50%.

## 3. RUL (Remaining Useful Life / Vida Útil Remanescente)
* **O que é:** Uma projeção dinâmica de quanto tempo (em anos) resta até que o SOH atinja a marca de 80%.
* **Como é calculado:** O algoritmo realiza uma regressão linear dividindo a capacidade degradável que ainda resta pela média do dano acumulado auferido por mês/ano desde o início térmico da simulação. 

---

## 4. O Paradoxo do Throughput vs. Energia Física

Existem duas formas primárias de medir a energia processada por um BESS. Elas resultam em valores bastante defasados entre si no BESx por motivações físicas da Teoria de Fadiga:

### 4.1. Energia de Carga e Descarga (Medidor Físico)
Medem o fluxo contínuo bidirecional que cruza as fronteiras do inversor (AC).
* **Cálculo:** Integração de Riemann padrão. O sistema varre ponto a ponto no tempo (`dt`) somando toda a `Potencia_CA` positiva na variável de Carga e a negativa na variável de Descarga.
* **Características:** Inclui ineficiências transitorias, calor dissipado por efeito Joule na célula interna e perdas de chaveamento elétrico no Inversor. Tudo isso "gira o relógio de luz", mas não entra como ciclagem do íon de lítio.

### 4.2. EFC e Throughput (Desgaste Equivalente)
Medem o desgaste na estrutura físico-química dos eletrodos, usando o algoritmo de fluxo de chuva (*Rainflow*).
* **EFC (Equivalent Full Cycles):** O número exato de oscilações de SOC profundas (DOD). 4 microciclos de 25% DOD formam matematicamente 1 EFC.
* **Throughput (MWh):** EFC multiplicado pela Capacidade Nominal da Bateria. Mede quantos miliampères-hora o sistema "esticou e comprimiu" fisicamente no catodo. Representa energia eletroquímica transitada, isolada da termodinâmica do ar-condicionado ou inversor.

### Conclusão do Paradoxo:
É **esperado e matematicamente correto** no BESx que o `Throughput < (Energia de Carga + Descarga)`. O primeiro mede desgaste de eletrodo filtrado por sinal; os outros medem potência total da usina (integrando atritos bidirecionais).

---

## 5. A Diferença de 25% (Rendimento DC-AC / RTE)

Em várias simulações foi atestado um *gap* crônico onde a bateria consome significativamente mais Energia de Carga do que devolve em Energia de Descarga de volta para a rede (~25% de diferença).

### Justificativas Implementadas no Motor:
1. **Perdas de Conversão (Inversor / PCS):** 
   Na configuração base atual, `rendimento_pcs = 0.88` (88%). Ao carregar, puxa-se energia extra da rede para bater a cota interna. Ao descarregar, apenas 88% do que sai da química chega nos fios AC. Isso afunda a o rendimento cíclico de "ida e volta" (RTE - Round Trip Efficiency) para a casa dos `0.88 * 0.88 = ~77,4%`.

2. **Resistência Interna ($R_s$) e Limite Terminal:**
   A equação de evolução `v_term_estimada = v_ocv_banco + (corrente_banco * rs_banco)` garante que, para injetar corrente de carga em polos resistivos, a tensão empurra para cima (pedindo mais W de pico da rede). Durante a descarga, a corrente derruba a tensão, rebaixando a área (MWh) exportada.

A junção de `~23%` de perdas exclusivas via Ponte AC/DC acrescidas de `2% a 4%` dissipados na resistência ôhmica em forma de calor validam uma Eficiência Eletroquímica Final de cerca de 70% a 75% da usina, perfeitamente de acordo com plantas reais de armazenamento pesado sem condicionamento auxiliar isolado. Seletivamente, o gap é mitigável alterando a variável `rendimento_pcs` em `config.py`.
