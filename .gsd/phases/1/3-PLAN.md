---
phase: 1
plan: 3
wave: 2
---

# Plan 1.3: EMS Execution and Heuristic SOC

## Objective
Wire the validation and strategy execution sequentially within `EMSManager`, and calculate the heuristic SOC output for the preview UI (REQ-11).

## Context
- .gsd/SPEC.md
- src/besx/application/ems/ems_manager.py
- src/besx/application/ems/ems_engine.py

## Tasks

<task type="auto">
  <name>Implement EMSManager run execution</name>
  <files>src/besx/application/ems/ems_manager.py</files>
  <action>
    - Update `EMSManager.run(self, df_carga: pd.DataFrame, time_col: str, load_col: str, **kwargs) -> pd.DataFrame` to execute constraints.
    - Step 1: Call `self.validate_and_prepare_input`.
    - Step 2: Loop over `self.strategies`. Although V1 enforces exactly 1 strategy in UI, iterate across the list and call `execute()` passing the validated `df` and `self.bess_ems`. Note: multiple strategies may overwrite `Potencia_Bateria_W` or chain it, define a basic chaining approach.
    - Step 3: Integrate the resulting `Potencia_Bateria_W` to calculate a heuristic SOC curve (REQ-11):
      - `Energy_Wh[t] = Energy_Wh[t-1] - (Potencia_Bateria_W[t] * dt_hours)`
      - `SOC[%] = Energy_Wh / capacidade_nominal_wh * 100`
      - Append `SOC_Heuristico` to the output DataFrame.
    - Step 4: Calculate and append simple summary metrics (Energy moved, peak shaved).
  </action>
  <verify>python -c "from besx.application.ems.ems_manager import EMSManager"</verify>
  <done>run() produces a DataFrame containing original timestamp, Potencia_Bateria_W, and SOC_Heuristico.</done>
</task>

## Success Criteria
- [ ] `EMSManager.run()` executes the configured strategies sequentially.
- [ ] Heuristic SOC curve is correctly calculated and bound between min/max limits.
- [ ] Final output conforms perfectly to the upstream Preview requirements.
