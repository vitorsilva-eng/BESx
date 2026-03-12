---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: EMS Core & Strategies

## Objective
Develop the underlying `EMSManager` structure and strategy wrappers to provide a future-proof foundation for multiple EMS algorithms, supporting REQ-09.

## Context
- .gsd/SPEC.md
- .gsd/ARCHITECTURE.md
- src/besx/application/ems/ems_engine.py

## Tasks

<task type="auto">
  <name>Create BaseStrategy and Concrete Strategies</name>
  <files>src/besx/application/ems/ems_manager.py</files>
  <action>
    - Create a new file `src/besx/application/ems/ems_manager.py`.
    - Import `BessEMS` from `ems_engine.py`.
    - Define an abstract base class `BaseStrategy` with an abstract method `execute(self, df_carga: pd.DataFrame, bess_ems: BessEMS, **kwargs) -> pd.DataFrame`.
    - Create `LoadShiftingStrategy` that inherits from `BaseStrategy` and calls `bess_ems.gerar_perfil_load_shifting(...)`.
    - Create `PeakShavingStrategy` that inherits from `BaseStrategy` and calls `bess_ems.gerar_perfil_peak_shaving(...)`.
  </action>
  <verify>python -c "from besx.application.ems.ems_manager import BaseStrategy, LoadShiftingStrategy, PeakShavingStrategy"</verify>
  <done>BaseStrategy ABC and both concrete wrappers are defined and importable without syntax errors.</done>
</task>

<task type="auto">
  <name>Create EMSManager Skeleton</name>
  <files>src/besx/application/ems/ems_manager.py</files>
  <action>
    - Define the `EMSManager` class in the same file.
    - Setup `__init__(self, strategies: list[BaseStrategy], p_bess_max_w: float, capacidade_nominal_wh: float)`.
    - Initialize an internal `BessEMS` instance using the provided BESS parameters.
    - Define a placeholder `run(self, df_carga: pd.DataFrame, **kwargs) -> pd.DataFrame` method.
  </action>
  <verify>python -c "from besx.application.ems.ems_manager import EMSManager"</verify>
  <done>EMSManager is defined and instantiated via a test import.</done>
</task>

## Success Criteria
- [ ] `EMSManager` constructor accepts a list of `BaseStrategy` instances (fulfilling REQ-09).
- [ ] Both `LoadShiftingStrategy` and `PeakShavingStrategy` wrap original `BessEMS` behavior properly.
