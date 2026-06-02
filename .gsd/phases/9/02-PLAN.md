---
phase: 9
plan: 2
wave: 2
depends_on: [9.1]
files_modified:
  - src/besx/infrastructure/ui/streamlit/pages/step_rules.py
autonomous: false
user_setup: []
must_haves:
  truths:
    - "Streamlit UI features a combined strategy parameter entry panel"
    - "Preview execution is fully wire-connected to CombinedStrategyLSPS"
    - "Exporting xlsx and injecting pickle formats continues working properly for Combined"
  artifacts:
    - "step_rules.py rendered combined strategy UI controls"
---

# Plan 9.2: Combined EMS Dashboard Integration

<objective>
Integrate the Combined Load Shifting & Peak Shaving strategy into the Streamlit dashboard user interface.

Purpose: Allow users to visually configure, preview, analyze and commit the combined strategy.
Output: Streamlit UI page updates with side-by-side controls and interactive plotly comparison charts.
</objective>

<context>
Load for context:
- .gsd/phases/9/01-PLAN.md
- src/besx/infrastructure/ui/streamlit/pages/step_rules.py
</context>

<tasks>

<task type="auto">
  <name>Integrate Combined UI parameters and inputs</name>
  <files>src/besx/infrastructure/ui/streamlit/pages/step_rules.py</files>
  <action>
    1. Add `"Combined (LS + PS)"` to the `st.radio` for strategy selection.
    2. Add conditional rendering block: if `"Combined (LS + PS)"` is active, render BOTH the Peak Shaving parameters (contract limit, safety margins) and the Load Shifting parameters (charge/discharge hour windows, holiday state and custom holidays).
    3. Pass consolidated parameter payload (as kwargs) when calling `ems_manager.run()`.
    Ensure all elements respect the streamlit width settings (use `width='stretch'` or `width='content'` as per project rules, avoid `use_container_width`).
    AVOID: using print statements. Use logging library if debug needed.
  </action>
  <verify>Launch streamlit and verify that the Combined option appears and parameters render without UI bugs</verify>
  <done>User inputs for both strategies render successfully when Combined is selected.</done>
</task>

<task type="checkpoint:human-verify">
  <name>Verify Dashboard Preview and Data Injection</name>
  <files>src/besx/infrastructure/ui/streamlit/pages/step_rules.py</files>
  <action>
    1. Upload a valid consumer telemetry file (e.g. `dadosnovos.csv`).
    2. Configure the Combined strategy (e.g. Peak Limit = 100kW, Margins, Charge 22h-17h, Discharge 18h-21h).
    3. Click on 'Gerar Preview e Validar Estratégia'.
    4. Confirm that the plotly chart shows the peaks shaved below the limit and load shifted from on-peak hours.
    5. Click 'Injetar para Simulação' and verify that BESS injection works and the pickle file is successfully saved.
  </action>
  <verify>Plotly chart shows combined peaks shaved and load shifted. Injected banner confirms success.</verify>
  <done>Combined dispatcher works end-to-end, validated visually by the user.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] UI works gracefully with no exceptions.
- [ ] Plotly dispatch chart displays correct active power curves.
- [ ] Exporting and Simulation Commit behaves as expected.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
