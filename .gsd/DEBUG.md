---
status: resolved
trigger: "/GSD Debugger colocando no sistema via dashboard estamos encontrando um pico de carga de 0,2kW..."
created: 2026-06-02T00:34:00Z
updated: 2026-06-02T00:34:05Z
---

## Current Focus
hypothesis: The user-selected telemetry column 'kWh fornecido' is in integrated energy units (kWh per 15-minute interval). Since the EMSManager did not map the user-selected 'unit_type' radio choice ("Energia (Wh/kWh)") to the validation pipeline nor execute the automatic heuristic detection, the values were copied verbatim to 'Carga_W' and treated directly as power in Watts. Thus, a value of 67.2 kWh was treated as 67.2 W (0.0672 kW), explaining the extremely small peak (0.2 kW) and total energy metrics (797 kWh instead of ~3,200,000 kWh).
test: Programmatically and visually verify unit conversions and auto-scaling.
expecting: Real telemetry values are converted to average active power in Watts: P(W) = E(kWh) * 1000 / dt_median(h).
next_action: None — successfully resolved.

## Symptoms
expected: Peak load of ~739.2 kW and total monthly projections of thousands of kWh.
actual: Peak load of 0.2 kW, monthly projection of 64 kWh.
errors: Verbatim metrics magnitude compression.

## Eliminated
- hypothesis: The columns were read in raw format incorrectly.
  evidence: Raw Excel reading works perfectly. The bug was in unit normalization logic.

## Evidence
- checked: `src/besx/application/ems/ems_manager.py`
  found: `df['Carga_W'] = df[load_col]` copied values directly without converting Wh/kWh to Watts.
  implication: Verified that REQ-08 was missing from the implementation.
- checked: `src/besx/infrastructure/ui/streamlit/pages/step_rules.py`
  found: `unit_type` selected in UI was not being saved in `st.session_state` nor passed to `ems_manager.run()`.
  implication: Missing state integration.

## Resolution
root_cause: Verbatim copy of raw energy values as power (missing implementation of requirement REQ-08).
fix:
1. Implemented robust heuristic detection and manual override conversion inside `EMSManager.validate_and_prepare_input` (scaling Wh/kWh/kW to Watts using the median `dt_val`).
2. Integrated `ems_unit_type` state variable inside Streamlit page `step_rules.py` and passed `is_energy` argument to the manager.
3. Added strict visual warnings (`st.warning`) in the UI when auto-conversion or auto-scaling is applied heuristic-wise.
verification: Complete pytest suite returns 100% GREEN. CINDACTA real telemetry script execution outputs exactly the expected commercial magnitude: 739.20 kW peak and zero exceedances.
