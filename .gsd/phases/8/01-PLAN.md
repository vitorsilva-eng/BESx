---
phase: 8
plan: 1
wave: 1
---

# Plan 8.1: PFC UI Controls & Logic Integration

## Objective
Implement the user interface controls for Power Factor Correction (PFC) in the EMS preview and integrate the strategy into the execution pipeline.

## Context
- .gsd/ROADMAP.md
- .gsd/DECISIONS.md
- .gsd/phases/8/RESEARCH.md
- src/besx/infrastructure/ui/streamlit/pages/step_rules.py
- src/besx/application/ems/ems_manager.py

## Tasks

<task type="auto">
  <name>Add PFC to Strategy Selector</name>
  <files>src/besx/infrastructure/ui/streamlit/pages/step_rules.py</files>
  <action>
    Modify the "🎯 Estratégia de Despacho" section to include "Power Factor Correction" as an option in the `st.radio` selector.
    Add conditional inputs when PFC is selected:
    - Target Power Factor (`pf_target`): Number input between 0.8 and 1.0 (default 0.98).
    - Inverter Capacity (`s_max_va`): Although eventually from Step 2, for this preview, add a default number input (e.g., 125000 VA).
  </action>
  <verify>Run the dashboard and check if "Power Factor Correction" appears in the radio button and shows the correct inputs when selected.</verify>
  <done>PFC is selectable and inputs are visible in the UI.</done>
</task>

<task type="auto">
  <name>Integrate PFC Strategy into Runner</name>
  <files>src/besx/infrastructure/ui/streamlit/pages/step_rules.py</files>
  <action>
    Update the `ems_manager` execution logic in the "📊 Gerar Preview" button callback:
    - Import `PowerFactorCorrectionStrategy` from `besx.application.ems.ems_manager`.
    - If `strategy_name == "Power Factor Correction"`, instantiate `PowerFactorCorrectionStrategy` and add it to `ems_manager.strategies`.
    - Pass `pf_target` and `s_max_va` (converted to float) into the `kwargs` for the `ems_manager.run` call.
  </action>
  <verify>Check logs or session state to ensure `ems_manager.run` is called with the correct strategy and parameters when PFC is selected.</verify>
  <done>EMS Manager executes the PFC strategy when selected in the UI.</done>
</task>

## Success Criteria
- [ ] PFC is an available dispatch strategy in the UI.
- [ ] Target PF and Inverter Capacity are configurable.
- [ ] Simulation generates reactive power dispatch data in the result DataFrame.
