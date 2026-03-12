# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v1.0 (EMS Manager Integration)

## Must-Haves (from SPEC)
- [x] Strict CSV Data Validator
- [x] Future-proof EMSManager Core class
- [x] Standalone EMS Preview UI (Charts & Metrics)
- [x] Commit-to-Simulation flow

## Phases

### Phase 1: Input Validation & EMSManager Core
**Status**: ✅ Complete
**Objective**: Develop the rigorous data ingestion pipeline and the underlying `EMSManager` structure (`src/besx/application/ems/ems_manager.py`), including the `BaseStrategy` ABC and concrete wrappers for Load Shifting and Peak Shaving.
**Requirements**: REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-11

### Phase 2: EMS Preview UI
**Status**: ✅ Complete
**Objective**: Create the Streamlit interface that handles file uploads, allows exclusive strategy selection, and graphs the heuristic outcomes (Power, SOC, Metrics).
**Requirements**: REQ-01, REQ-02, REQ-10

### Phase 3: Simulation Pipeline Integration
**Status**: ✅ Complete
**Objective**: Wire the "Commit" action from the Preview UI directly into the `SimulationManager`, ensuring compatibility across the mathematical engines. Explicitly discuss and decide on serialization (in-memory vs. `.mat` file) before implementation.
**Requirements**: REQ-03
