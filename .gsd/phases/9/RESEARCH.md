---
phase: 9
level: 2
researched_at: 2026-06-01
---

# Phase 9 Research: Combined EMS Algorithm (Load Shifting & Peak Shaving)

## Questions Investigated

1. **How should conflicts in dispatch priority be resolved between Peak Shaving and Load Shifting?**
   - *Conflict:* During peak demand periods, Peak Shaving demands battery discharge, while Load Shifting might be in a charging window or idle. Conversely, during high-tariff discharge windows, Load Shifting wants full discharge, but Peak Shaving must guarantee demand limits.
   - *Resolution:* Demand limit safety (Peak Shaving) must always take mathematical precedence. A breach of contracted demand limits results in financial penalties (ultrapassagem de demanda). Thus, if $P_{load}(t) > P_{limit}$, the battery *must* discharge the difference to maintain the grid connection at or below the effective limit, regardless of whether $t$ is inside a Load Shifting charge, discharge, or idle window.

2. **How to design a unified, vectorized mathematical model for $O(1)$ temporal dispatch calculation?**
   - *Model Design:* Formulate a single mathematical algorithm that takes all relevant variables ($P_{load}(t)$, $P_{limit}$, windows, calendars) and processes them in a single step using NumPy vectorized operations, avoiding slow Python loops.

3. **How to structure the strategy pattern in `EMSManager` to support this stacked behavior?**
   - *Structure:* Maintain the existing clean architecture. Rather than hacking sequential strategy execution (which currently overwrites the BESS active power setpoints), we will implement a dedicated concrete strategy `CombinedStrategyLSPS` that encapsulates the joint logic and calls a dedicated vectorized dispatcher in `BessEMS`.

4. **How to adapt the Streamlit UI (`step_rules.py`) to allow intuitive configuration of both strategies simultaneously?**
   - *UI Adaptation:* Expand the single strategy selection radio button to include `"Combined (LS + PS)"`. When selected, conditionally render input panels for *both* strategies (demands, safety margins, windows, holiday rules) and pass them as a single parameter payload to the EMS engine.

---

## Findings

### Priority & Mathematical Formulation
Let:
- $P_{load}(t)$ be the consumer load at time $t$ (in Watts).
- $P_{limit\_eff}$ be the effective contract limit (in Watts), calculated as:
  $$P_{limit\_eff} = \left(P_{limit\_kw} - P_{margin\_kw} - \left(P_{limit\_kw} \times \frac{P_{margin\_pct}}{100.0}\right)\right) \times 1000.0$$
- $is\_charge(t)$ and $is\_discharge(t)$ be boolean masks for the Load Shifting time windows.
- $is\_weekday\_valid(t)$ be a boolean mask for business days (excluding weekends and regional holidays).

The target battery dispatch $P_{bess}(t)$ (where positive represents charging/load and negative represents discharging/generation) is defined as:

$$\begin{cases}
P_{limit\_eff} - P_{load}(t), & \text{if } P_{load}(t) > P_{limit\_eff} \quad \text{(Peak Shaving Discharge)} \\
-P_{load}(t), & \text{if } P_{load}(t) \le P_{limit\_eff} \text{ and } is\_discharge(t) \text{ and } is\_weekday\_valid(t) \quad \text{(Load Shifting Discharge)} \\
\max\left(0, P_{limit\_eff} - P_{load}(t)\right), & \text{if } P_{load}(t) \le P_{limit\_eff} \text{ and } is\_charge(t) \text{ and } is\_weekday\_valid(t) \quad \text{(Load Shifting Charge)} \\
0, & \text{otherwise (Idle Period)}
\end{cases}$$

This mathematical logic perfectly synthesizes both behaviors:
- **Peak Shaving takes absolute priority:** If demand is breached, the battery discharges to keep the grid load at $P_{limit\_eff}$.
- **Load Shifting fills active windows during non-peak events:** It discharges fully to shave expensive on-peak consumption, and charges during off-peak windows, respecting the available grid connection headroom (demand limit).

### Streamlit Integration and Charting
The dashboard will display the three power curves together:
- *Original Load* ($P_{load}$)
- *Battery Dispatch Setpoint* ($P_{bess}$)
- *Adjusted Grid Load* ($P_{grid} = P_{load} + P_{bess}$)
This allows immediate visual validation of:
1. Peaks clipped precisely at $P_{limit\_eff}$ (Peak Shaving).
2. Load shifted from on-peak to off-peak hours (Load Shifting).

---

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Strategy Pattern Hook** | `CombinedStrategyLSPS` class | Keeps core clean architecture modular, maintains isolated wrappers for academic comparison, and implements the math in a unified execution. |
| **Priority Hierarchy** | Peak Shaving > Load Shifting | Contractual security and penalty avoidance must dictate priority over energy arbitrage savings. |
| **Vectorization Library** | NumPy Masking & Vectorization | Preserves $O(1)$ computation time, satisfying real-time Streamlit recalculation constraints. |

---

## Patterns to Follow
- **Vectorized Masking:** Use NumPy logical arrays (`&`, `|`, `~`) to perform element-wise evaluations.
- **Unified Logger:** Do not use `print()`. Use the project's native `logger.info()` and `logger.warning()`.
- **Strict Typing:** All new methods and classes must contain complete Type Hints.

## Anti-Patterns to Avoid
- **Iterative Python Loops (`for index, row in df.iterrows()`):** Extremely slow, will choke the CPU on long telemetries, causing UI lags in Streamlit.
- **Linear Damage Accumulation:** The mathematical battery physics engine downstream expects precise cyclic transitions. We must ensure the EMS setpoint doesn't introduce sharp artificial numeric discontinuities.

---

## Dependencies Identified
No new packages are needed. The existing dependencies are sufficient and locked:
| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 2.1.4 | Data processing and ingestion |
| numpy | 1.26.2 | Vectorized algebraic computations |
| holidays | 0.40 | Regional calendar verification |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| **Simultaneous Charge/Discharge Windows overlap** | Add safety validation inside `CombinedStrategyLSPS` that detects overlapping hours and logs a warning or raises a value error to prevent mathematical oscillates. |
| **Battery capacity exhaustion (Physical boundary)** | The BESS physical limitations (SOC bounds, maximum power capacity) are handled downstream by the `BatterySimulator`. The EMS target profile remains commercial (setpoint target). We will clearly document this isolation in the class docstrings. |

---

## Ready for Planning
- [x] Questions answered
- [x] Approach selected
- [x] Dependencies identified
