# REQUIREMENTS.md

## Format
| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| REQ-01 | **EMS Preview UI**: Display pre/post EMS power charts, heuristic SOC, and summary KPIs (energy, peak, cycles). | SPEC Goal 1 | Pending |
| REQ-02 | **Preview Isolation**: Preview generation must strictly bypass deep degradation simulations (Rainflow/PLECS). | SPEC Goal 1 | Pending |
| REQ-03 | **Commit Pipeline**: Button to inject `Potencia_Bateria_W` into the `SimulationManager` replacing the original input. | SPEC Goal 2 | Pending |
| REQ-04 | **Validation - Datetime**: Parse datetime64 or fail completely. | SPEC Goal 3 | Pending |
| REQ-05 | **Validation - Numeric**: Fails completely if payload contains non-numeric values. | SPEC Goal 3 | Pending |
| REQ-06 | **Validation - NaN**: Abort and point to affected lines if NaNs are found (no interpolation). | SPEC Goal 3 | Pending |
| REQ-07 | **Validation - dt Uniformity**: Alert if dt variance exceeds ±5%. | SPEC Goal 3 | Pending |
| REQ-08 | **Validation - kWh inference**: Detect if input is kWh (based on dt vs value magnitude), auto-convert to kW, and display explicit UI warning. | SPEC Goal 3 | Pending |
| REQ-09 | **API Design**: `EMSManager.run` must accept `strategies: list[BaseStrategy]`. | SPEC Goal 4 | Pending |
| REQ-10 | **UI Design**: Strategy selection must use `st.radio` to restrict length of strategies list to exactly 1. | SPEC Constraint | Pending |
| REQ-11 | **Heuristic SOC**: Calculate heuristic SOC via energy integration directly within `EMSManager` for the preview. | SPEC Goal 1 | Pending |
