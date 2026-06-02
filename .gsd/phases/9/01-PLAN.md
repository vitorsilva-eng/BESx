---
phase: 9
plan: 1
wave: 1
depends_on: []
files_modified:
  - src/besx/application/ems/ems_engine.py
  - src/besx/application/ems/ems_manager.py
  - tests/test_ems_combined.py
autonomous: true
user_setup: []
must_haves:
  truths:
    - "Combined strategy executes without loops using vectorized NumPy masking"
    - "Peak shaving takes absolute mathematical priority in any time window"
    - "Load shifting charges inside charge windows respecting demand safety headroom"
    - "Load shifting discharges inside discharge windows on business days"
  artifacts:
    - "tests/test_ems_combined.py exists with comprehensive verification edge cases"
---

# Plan 9.1: Combined EMS Dispatch Core & Tests

<objective>
Implement and unit test the core mathematical dispatch logic for the combined Load Shifting and Peak Shaving strategy inside the BessEMS engine and its EMSManager wrapper.

Purpose: Provide a prioritized, vectorized combined dispatch that protects customer contract limits while maximizing energy arbitrage.
Output: Vectorized engine dispatch method, EMSManager strategy wrapper, and pytest suite.
</objective>

<context>
Load for context:
- .gsd/phases/9/RESEARCH.md
- src/besx/application/ems/ems_engine.py
- src/besx/application/ems/ems_manager.py
</context>

<tasks>

<task type="auto">
  <name>Create combined EMS unit tests (Red Phase)</name>
  <files>tests/test_ems_combined.py</files>
  <action>
    Write a complete unit test suite for the new Combined strategy using pytest and pandas/numpy.
    Include test cases for:
    1. Peak Shaving priority during off-peak and on-peak hours.
    2. Load Shifting charging respect to demand limit headroom.
    3. Load Shifting discharge on business days and idle state on holidays/weekends.
    Ensure all tests fail initially since the implementation does not exist yet.
    AVOID: hardcoding absolute paths. Use relative imports and mock pandas DataFrames dynamically.
  </action>
  <verify>pytest tests/test_ems_combined.py</verify>
  <done>pytest runs and all tests fail due to missing implementation in the core files.</done>
</task>

<task type="auto">
  <name>Implement Combined EMS logic (Green Phase)</name>
  <files>src/besx/application/ems/ems_engine.py, src/besx/application/ems/ems_manager.py</files>
  <action>
    1. Implement the vectorized `gerar_perfil_combinado_ls_ps` method inside `BessEMS` class in `ems_engine.py` following the mathematical model from RESEARCH.md.
    2. Implement `CombinedStrategyLSPS` class inheriting from `BaseStrategy` inside `ems_manager.py` that maps the inputs and calls `gerar_perfil_combinado_ls_ps`.
    Ensure all code has strict type hints, Google/NumPy style docstrings, and utilizes `logger` instead of `print()`.
    AVOID: loops over DataFrame rows. All calculations must be element-wise using NumPy vectorize masking.
  </action>
  <verify>pytest tests/test_ems_combined.py</verify>
  <done>All unit tests pass successfully (Green phase).</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] Pytest suite returns 100% success for all Edge Cases.
- [ ] No performance regression on dataset processing.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
