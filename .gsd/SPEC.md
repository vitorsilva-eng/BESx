# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
Integrate the existing Load Shifting and Peak Shaving algorithms into a cohesive EMS Manager UI workflow. This workflow will feature two clear stages: a standalone preview stage for visualizing battery dispatch behavior and heuristics (without mathematical degradation simulation), and a commit stage that seamlessly injects the planned load profile into the core SimulationManager downstream.

## Goals
1. **EMS Preview (Standalone)**: Implement a UI stage where `BessEMS` processes the load curve and displays a preview: (a) power comparison chart (original load vs. post-EMS load vs. battery profile), (b) heuristically estimated SOC curve (computed via energy integration within the `EMSManager`), and (c) summary metrics (energy moved in kWh, peak shaved in kW, estimated cycle count).
2. **Commit to Simulation**: Implement a mechanism to pass the resulting `Potencia_Bateria_W` curve back into the `SimulationManager` pipeline, replacing the default naive input curve, without altering downstream degradation logic. An explicit architectural decision regarding serialization (in-memory vs `.mat` file dump) will be made in Phase 3.
3. **Strict Input Validation**: Build a robust data ingestion layer that checks for datetime format, numeric types, rejects NaNs, verifies time-step (dt) uniformity (±5%), and heuristically detects/converts kWh to kW.
4. **Future-proof API**: Architect the new `EMSManager` (explicit path: `src/besx/application/ems/ems_manager.py`) to accept a list of strategies (`EMSManager.run(strategies: list[BaseStrategy], df_carga, params) -> EMSResult`), even though V1 UI will enforce a single selection. This includes implementing the `BaseStrategy` ABC and the two concrete wrappers for Load Shifting and Peak Shaving during Phase 1.

## Non-Goals (Out of Scope)
- Creating new EMS dispatch algorithms (e.g., dynamic arbitrage, self-consumption).
- Multi-strategy stacking in the UI (executing them concurrently). This is reserved for V2 to allow isolated mathematical validation for the research paper.

## Users
Battery researchers and engineers utilizing BESx to map empirical degradation who need to pre-condition their raw consumption time-series data using operational strategies.

## Constraints
- **Methodology**: Algorithms must be tested in absolute isolation; the UI must strictly use a `st.radio` (single selection) for the strategies.
- **Validation Blocks**: Any failure in datetime parsing, non-numeric checks, or NaN detection must explicitly block the execution and return a clear fatal warning to the user rather than interpolating or silently dropping data.

## Success Criteria
- [ ] Users can upload a target consumption curve (CSV) and view a realistic dispatch preview (charts + metrics) in seconds.
- [ ] Invalid CSV files are caught immediately by the validation pipeline with precise explanations.
- [ ] A generated EMS profile can be committed and successfully simulated within the existing PLECS or Python engine configurations.
