# Wave 1 Summary

- Implemented `BaseStrategy` ABC interface for EMS strategies.
- Developed `LoadShiftingStrategy` and `PeakShavingStrategy` wrappers referencing `BessEMS` algorithms.
- Created `EMSManager` skeleton to accept `strategies`, `p_bess_max_w`, and `capacidade_nominal_wh`.
- Built robust `validate_and_prepare_input` inside `EMSManager` capturing REQ-04 through REQ-08 rules (Datetime parsing, strictly numeric columns, explicit NaN rejection, dt variance checking, kWh heuristical inference with explicit warnings). All exceptions yield `ValueError` to halt simulation gracefully.
