---
phase: 7
plan: 2
wave: 2
depends_on: ["7.1"]
files_modified: ["src/besx/application/ems/ems_engine.py", "src/besx/application/ems/ems_manager.py"]
autonomous: true

must_haves:
  truths:
    - "BessEMS inclui função vetorizada gerar_perfil_power_factor_correction."
    - "A capacidade do inversor atua como limite real para a injeção reativa."
    - "PowerFactorCorrectionStrategy existe e pode ser injetada no array de estratégias do EMSManager."
  artifacts:
    - "src/besx/application/ems/ems_engine.py possui método de PFC."
    - "src/besx/application/ems/ems_manager.py exporta a nova estratégia."
---

# Plan 7.2: Implementação da Estratégia de Correção de Fator de Potência

<objective>
Implementar a rotina matemática de injeção reativa no `BessEMS` e envelopá-la na classe concreta `PowerFactorCorrectionStrategy`, respeitando os limites geométricos de potência aparente ($S^2 = P^2 + Q^2$).

Purpose: Fechar a entrega da Fase 6 fornecendo a funcionalidade de correção do fator de potência que aproveita as capacidades do PCS do BESS.
Output: Motor de EMS com cálculo de potência reativa (`Potencia_Reativa_Bateria_VAr`).
</objective>

<context>
Load for context:
- .gsd/phases/7/RESEARCH.md
- src/besx/application/ems/ems_engine.py
- src/besx/application/ems/ems_manager.py
</context>

<tasks>

<task type="auto">
  <name>Criar método matemático no BessEMS</name>
  <files>src/besx/application/ems/ems_engine.py</files>
  <action>
    Adicionar `gerar_perfil_power_factor_correction(self, df_carga, pf_target, s_max_va) -> pd.DataFrame`.
    A função deve ler `Carga_W`, `Carga_VAr` e `Potencia_Bateria_W` (Potência Ativa já despachada).
    Passos:
    1. Calcular a potência reativa alvo ($Q_{alvo}$) usando $PF_{target}$ sobre a carga final ($P_{carga} + P_{bess}$).
    2. Calcular o VAr necessário da bateria ($Q_{req} = Q_{alvo} - Q_{carga}$).
    3. Calcular a sobra de potência aparente do inversor: $Q_{disp} = \sqrt{\max(0, S_{max}^2 - P_{bess}^2)}$.
    4. Aplicar clipe: $Q_{bess} = \text{clip}(Q_{req}, -Q_{disp}, Q_{disp})$.
    Retornar um DataFrame com a coluna `Potencia_Reativa_Bateria_VAr`.
    AVOID: Omitir o limite $Q_{disp}$. O inversor não pode fornecer reativo se já estiver no máximo de potência ativa.
  </action>
  <verify>python -m py_compile src/besx/application/ems/ems_engine.py</verify>
  <done>Método vetorizado existe e processa $S_{max}$ corretamente.</done>
</task>

<task type="auto">
  <name>Criar o wrapper PowerFactorCorrectionStrategy</name>
  <files>src/besx/application/ems/ems_manager.py</files>
  <action>
    Criar a classe `PowerFactorCorrectionStrategy(BaseStrategy)`.
    No seu método `execute()`, chame `bess_ems.gerar_perfil_power_factor_correction` lendo os kwargs `pf_target` e `s_max_va`.
    Se `s_max_va` não vier em kwargs, pegue-o da instância de `bess_ems` ou defina um fallback inteligente (ex: log warning e usa max_p).
    Ao integrar no `EMSManager.run()`, garanta que a coluna `Potencia_Reativa_Bateria_VAr` seja incorporada ao DataFrame processado final, sem sobrescrever `Potencia_Bateria_W`.
    AVOID: Misturar `Potencia_Reativa_Bateria_VAr` com `Potencia_Bateria_W`. O DataFrame de saída deve conter ambas.
  </action>
  <verify>python -c "from src.besx.application.ems.ems_manager import PowerFactorCorrectionStrategy"</verify>
  <done>Nova estratégia pronta e isolada.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] O limite geométrico ($S^2$) impede injetar reativo se a bateria está na potência máxima ativa.
- [ ] As 2 colunas distintas (Watts e VArs da Bateria) coexistem na saída.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
