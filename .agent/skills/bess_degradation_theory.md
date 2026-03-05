---
name: Teoria de Degradação BESS
description: Fundamentação física e modelos matemáticos de degradação de baterias de Lítio.
---

# Teoria de Degradação BESS (Battery Energy Storage Systems)

Este documento serve como a base de conhecimento científico para o agente lidar com cálculos de SOH (State of Health) e vida útil no simulador BESx.

## 1. Mecanismos de Degradação

A degradação de baterias Li-ion é um processo complexo dividido em dois pilares principais:

### 1.1 Degradação por Calendário (Calendar Aging)

Ocorre independentemente do uso, devido ao tempo e condições de armazenamento.

- **Principais Influentes:**
  - **Temperatura (T):** Segue a lei de Arrhenius. Temperaturas elevadas aceleram reações químicas indesejadas na interface anodo-eletrólito (SEI layer).
  - **Estado de Carga (SoC):** Potenciais de eletrodo elevados (SoC alto) aumentam a instabilidade química.

### 1.2 Degradação por Ciclagem (Cycle Aging)

Ocorre devido ao fluxo de corrente (carga e descarga).

- **Principais Influentes:**
  - **Profundidade de Descarga (DoD):** Ciclos mais profundos causam maior estresse mecânico.
  - **Corrente (C-rate):** Altas taxas de carga/descarga aumentam o aquecimento Joule e podem causar deposição de lítio metálico (Lithium Plating).

## 2. Modelagem Matemática

### 2.1 Modelo de Arrhenius para Calendar Aging

A taxa de degradação $\dot{d}_{cal}$ pode ser aproximada por:
$$\dot{d}_{cal} = A \cdot e^{-\frac{E_a}{R \cdot T}} \cdot f(SoC) \cdot t^{0.5}$$
Onde $E_a$ é a energia de ativação e $R$ a constante dos gases.

### 2.2 Modelo de Fadiga (Wöhler-like) para Cycle Aging

Baseado no throughput de energia ou contagem de ciclos equivalentes:
$$L_{total} = L_{nom} \cdot (DoD)^{-\beta}$$

## 3. Parâmetros de Referência (LFP/NMC)

- **EOL (End of Life):** Geralmente definido quando $SOH = 80\%$.
- **Capacidade Nominal:** Medida em Ah ou kWh.
- **Raios de Operação Ideais:** $15\% < SoC < 85\%$ para maximização de vida útil.
