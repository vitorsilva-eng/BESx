---
phase: 8
plan: 2
wave: 1
---

# Plan 8.2: Quality Energy Visualization

## Objective
Implement dedicated visualizations for Reactive Power (VAr) and Power Factor (PF) to provide clear feedback on the PFC strategy results.

## Context
- .gsd/ROADMAP.md
- src/besx/infrastructure/visualization/plotly_plots.py
- src/besx/infrastructure/ui/streamlit/pages/step_rules.py

## Tasks

<task type="auto">
  <name>Create Quality Visualization Plots</name>
  <files>src/besx/infrastructure/visualization/plotly_plots.py</files>
  <action>
    Add two new plot functions:
    1. `plot_reactive_power_comparison`: Shows `Carga_VAr` (Original) vs `Carga_Ajustada_VAr` (Network view) and `Potencia_Reativa_Bateria_VAr`.
    2. `plot_power_factor_comparison`: Shows `Carga_FP` vs `Carga_Ajustada_FP`. Include a horizontal dashed line at 0.92 (legal limit) and another at the `pf_target` if provided.
  </action>
  <verify>Check the new functions exist and can be called with a sample DataFrame.</verify>
  <done>Plotly functions for VAr and FP are implemented.</done>
</task>

<task type="auto">
  <name>Implement Qualidade Tab in Dashboard</name>
  <files>src/besx/infrastructure/ui/streamlit/pages/step_rules.py</files>
  <action>
    Modify the diagnostic tabs (around line 257) to add a fifth tab: "⚡ Qualidade (PFC)".
    Inside this tab:
    - Display the new Reactive Power comparison chart.
    - Display the Power Factor comparison chart.
    - Show metrics for "Worst Power Factor (Before vs After)".
  </action>
  <verify>Run the dashboard after a PFC simulation and verify if the "Qualidade" tab displays the charts correctly with real data.</verify>
  <done>PFC results are visually accessible in the "Qualidade" tab.</done>
</task>

## Success Criteria
- [ ] Dedicated tab for Quality/PFC metrics exists.
- [ ] Reactive Power chart clearly shows the battery compensation.
- [ ] Power Factor chart shows improvement towards the target.
