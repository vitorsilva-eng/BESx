# Wave 2 Summary

- Integrated `validate_and_prepare_input` directly into the `run()` execution flow.
- Added sequential execution of the assigned strategies over the validated DataFrame.
- Implemented heuristic SOC integration based on battery power and `dt` (REQ-11), ensuring saturation bounds according to defined capacity.
- Appended `Carga_Ajustada_W` to the final output for simpler plotting in the UI stage.
