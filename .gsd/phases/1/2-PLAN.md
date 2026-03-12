---
phase: 1
plan: 2
wave: 1
---

# Plan 1.2: Rigorous Data Ingestion Validation

## Objective
Implement strict CSV data validation methods inside `EMSManager` to prevent bad data from reaching the mathematical models (REQ-04 to REQ-08).

## Context
- .gsd/SPEC.md
- src/besx/application/ems/ems_manager.py

## Tasks

<task type="auto">
  <name>Implement Data Validation Pipeline</name>
  <files>src/besx/application/ems/ems_manager.py</files>
  <action>
    - Add a method `validate_and_prepare_input(self, df: pd.DataFrame, time_col: str, load_col: str) -> pd.DataFrame` to `EMSManager`.
    - Implement REQ-04: Ensure `time_col` can be parsed via `pd.to_datetime`. Raise ValueError if not.
    - Implement REQ-05: Ensure `load_col` is strictly numeric. Raise ValueError if not.
    - Implement REQ-06: Check for NaNs. If NaNs exist, raise ValueError detailing the affected line indices explicitly. Do not interpolate.
    - Implement REQ-07: Calculate dt (delta time) between rows. If variance exceeds ±5% of the median dt, log a warning via `logger.warning`.
    - Implement REQ-08: Add heuristic logic: if all values in `load_col` are significantly low relative to expected power output (e.g. median load_col * dt_hours is close to load_col conceptually), infer it might be kWh. Auto-convert kWh to kW and emit `logger.warning` explicitly describing the conversion.
  </action>
  <verify>python -m pytest tests/test_data_handler.py -k "validator" || echo "Skip if no tests yet"</verify>
  <done>The validation method enforces all 5 checks reliably and throws appropriate Exceptions instead of silent failures.</done>
</task>

## Success Criteria
- [ ] Datetime errors and NaNs throw fatal errors pointing to specific issues.
- [ ] dt nonuniformity generates warnings.
- [ ] kWh heuristic detection operates automatically with logged warnings.
