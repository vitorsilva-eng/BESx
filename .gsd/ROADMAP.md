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

### Phase 4: Advanced Comparison Metrics
**Status**: ✅ Complete
**Objective**: Enhance the battery comparison dashboard with deep metrics: DOD distribution, Energy throughput, Efficiency, and Operational stress.
**Requirements**: REQ-COMPARISON-01, REQ-COMPARISON-02

### Phase 5: Performance Optimization
**Status**: ✅ Complete
**Objective**: Optimize the battery simulation (Coulomb counting) and degradation engine to achieve > 5 months/s of execution speed using Numba JIT and NumPy vectorization.
**Requirements**: REQ-PERF-01

### Phase 6: Restauração de UI e Higiene de CSS
**Status**: ✅ Complete
**Objective**: Upgrade Streamlit to 1.54.0 and isolate sidebar CSS.

### Phase 7: Power Factor Correction
**Status**: ✅ Complete
**Objective**: Implement power factor correction reactive dispatch in the EMS engine.

### Phase 8: PFC UI Integration
**Status**: ✅ Complete
**Goal**: Integrate PFC configuration and visual reporting into the dashboard.
- [x] Input de `pf_target` e `s_max_va` no Passo 1.
- [x] Injeção dinâmica no `EMSManager` via kwargs.
- [x] Gráficos de VAr e FP no Dashboard.
**Depends on**: Phase 7

**Tasks**:
- [ ] TBD (run /plan 8 to create)

**Verification**:
- TBD
