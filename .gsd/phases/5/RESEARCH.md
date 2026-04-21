---
phase: 5
level: 2
researched_at: 2026-04-21
---

# Phase 5 Research: Performance Optimization

## Questions Investigated
1. **How much speedup can `numba.njit` provide for the `simular_soc_mes` loop?**
   - The loop has ~43k iterations. Numba can reduce this from ~0.9s to <0.05s by compiling the scalar math into LLVM machine code.
2. **What is the most efficient way to detect "idle" cycles using NumPy (vectorization)?**
   - Using `np.diff` to find constant SOC regions.
3. **Can we avoid redundant `picos_e_vales` (Rainflow simplification) calls?**
   - Yes, calculating it once in `DegradationEngine` and passing it to `dano_ciclo` and `stats_ops` prevents re-calculation.

## Findings

### Simulation Engine (Coulomb Counting)
The current loop in `battery_simulator.py` is pure Python. 
- **Bottleneck**: Individual array accesses and math operations inside the loop.
- **Recommendation**: Move the core loop into a sub-function decorated with `@njit(cache=True)`. All inputs for the numba function must be NumPy arrays or primitive types.

### Degradation Analysis
- **Bottleneck**: `iterrows()` in `dano_ciclo` and `dano_calendar`.
- **Recommendation**: Use vectorized operations like `df['C_fade'] = a * np.exp(b * df['soc'] * 100)`.
- **Bottleneck**: `ciclos_idle` uses a Python list builder.
- **Recommendation**: Use `np.diff` and `np.where` to find transition points.

## Decisions Made
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Acceleration Engine | Numba JIT | Best trade-off between performance (C-like) and maintenance (Python syntax). |
| Data Transfer | NumPy Arrays | Required for Numba and efficient vectorized math in NumPy. |
| Logic Refactoring | Single-pass simplification | Reduces CPU usage by eliminating redundant peak/valley searches. |

## Patterns to Follow
- Use `@njit` on performance-critical loops.
- Pass NumPy arrays, not Pandas Series, to Numba functions.
- Vectorize math formulas (`exp`, `sqrt`) whenever possible.

## Anti-Patterns to Avoid
- Avoid `.iterrows()` or `.apply()` on large dataframes.
- Avoid multiple calls to `picos_e_vales` for the same monthly data.

## Dependencies Identified
| Package | Version | Purpose |
|---------|---------|---------|
| numba | 0.61.0 | JIT compilation of the simulation loop. |
| numpy | 1.26.1 | Vectorized mathematical operations. |

## Risks
- **Numba Initialization**: The first call to a Numba function has a compilation overhead.
  - **Mitigation**: Use `cache=True` in `@njit`.
- **Mathematical Parity**: Optimized code might have small floating point differences.
  - **Mitigation**: Create `check_parity.py` to ensure MAE < 1e-6.

## Ready for Planning
- [x] Questions answered
- [x] Approach selected
- [x] Dependencies identified
