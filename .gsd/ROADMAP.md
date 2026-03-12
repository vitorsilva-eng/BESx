# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v1.0 (EMS Manager Integration)

## Must-Haves (from SPEC)
- [ ] Strict CSV Data Validator
- [ ] Future-proof EMSManager Core class
- [ ] Standalone EMS Preview UI (Charts & Metrics)
- [ ] Commit-to-Simulation flow

## Phases

### Phase 1: Input Validation & EMSManager Core
**Status**: ⬜ Not Started
**Objective**: Develop the rigorous data ingestion pipeline and the underlying `EMSManager` structure that bridges raw CSVs and the `BessEMS` algorithms.
**Requirements**: REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09

### Phase 2: EMS Preview UI
**Status**: ⬜ Not Started
**Objective**: Create the Streamlit interface that handles file uploads, allows exclusive strategy selection, and graphs the heuristic outcomes (Power, SOC, Metrics).
**Requirements**: REQ-01, REQ-02, REQ-10

### Phase 3: Simulation Pipeline Integration
**Status**: ⬜ Not Started
**Objective**: Wire the "Commit" action from the Preview UI directly into the `SimulationManager`, ensuring compatibility across the mathematical engines.
**Requirements**: REQ-03
