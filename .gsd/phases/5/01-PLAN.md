---
phase: 5
plan: 1
wave: 1
depends_on: []
files_modified: ["src/besx/domain/models/battery_simulator.py", "src/besx/domain/models/degradation_engine.py", "src/besx/domain/models/degradation_model.py"]
autonomous: true
user_setup: []

must_haves:
  truths:
    - "Simulação de 1 mês em Python leva menos de 0.1s (alvo: > 10 meses/s)"
    - "Paridade matemática mantida com MAE < 1e-6"
  artifacts:
    - "src/besx/domain/models/battery_simulator.py (Numba JIT)"
    - "src/besx/domain/models/degradation_model.py (Vectorized)"
    - "src/besx/domain/models/degradation_engine.py (Single-pass)"
---

# Plan 5.1: Performance Engine Overhaul

<objective>
Otimizar o motor de simulação e análise de degradação para atingir uma velocidade superior a 5 meses/s, utilizando compilação Numba JIT para o loop de Coulomb e vetorização NumPy para os modelos de dano.
</objective>

<context>
- .gsd/SPEC.md
- .gsd/phases/5/RESEARCH.md
- src/besx/domain/models/battery_simulator.py
- src/besx/domain/models/degradation_model.py
- src/besx/domain/models/degradation_engine.py
</context>

<tasks>

<task type="auto">
  <name>Implementar Simulação JIT (Numba)</name>
  <files>src/besx/domain/models/battery_simulator.py</files>
  <action>
    - Criar uma função `_coulomb_engine_numba` decorada com `@njit`.
    - Mover o loop de integração de `simular_soc_mes` para esta função.
    - Converter todos os parâmetros de entrada (OCV profiles, config constants) em arrays NumPy ou escalares primitivos compatíveis com Numba.
  </action>
  <verify>Rodar `scratch/profile_sim.py` e verificar redução no tempo de 'Simulation (Coulomb)'.</verify>
  <done>O loop principal de simulação agora roda via código compilado JIT.</done>
</task>

<task type="auto">
  <name>Vetorizar Ciclos Idle e Modelos de Dano</name>
  <files>src/besx/domain/models/battery_simulator.py, src/besx/domain/models/degradation_model.py</files>
  <action>
    - Refatorar `ciclos_idle` em `battery_simulator.py` para usar `np.diff` e `np.where` em vez de um loop `for`.
    - Refatorar `dano_ciclo` e `dano_calendar` em `degradation_model.py` para usar operações vetorizadas do NumPy em vez de `.iterrows()`.
  </action>
  <verify>Verificar se os resultados de dano permanecem idênticos aos originais.</verify>
  <done>Análises de degradação não possuem mais loops Python pesados ou iterações em DataFrames.</done>
</task>

<task type="auto">
  <name>Refatorar Fluxo da Engine para Único Passo</name>
  <files>src/besx/domain/models/degradation_engine.py</files>
  <action>
    - Alterar `calculate_degradation` para calcular `perfil_simp` e `idle_cycles_mes` uma única vez.
    - Passar esses valores processados para `dano_ciclo`, `dano_calendar` e `calcular_estatisticas_operacionais`.
  </action>
  <verify>Verificar log de execução e tempos no perfilamento.</verify>
  <done>Redundância eliminada. `picos_e_vales` é chamado apenas uma vez por mês.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] Execução de 240 meses em menos de 30 segundos.
- [ ] Script de paridade confirma erro próximo a zero contra o modelo antigo.
</verification>

<success_criteria>
- [ ] Velocidade sustentada de > 5 meses/s em hardware padrão.
</success_criteria>
