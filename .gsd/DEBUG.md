---
status: resolved
trigger: "NameError: name 'np' is not defined in step_rules.py"
created: 2026-05-04T23:35:50Z
updated: 2026-05-04T23:36:05Z
---

## Resolution
root_cause: `numpy` (as `np`) was used in the newly added PFC Quality tab logic but was not imported within the `render_step_rules` scope.
fix: Added `import numpy as np` inside `render_step_rules`.
verification: The app should now render the PFC tab correctly without NameError.

## Symptoms
expected: "Qualidade (PFC)" tab renders charts and metrics.
actual: App crashes with `NameError: name 'np' is not defined`.
errors:
```
File "C:\Users\Ledax\OneDrive - LEDAX\Área de Trabalho\BESx\src\besx\infrastructure\ui\streamlit\pages\step_rules.py", line 310, in render_step_rules
    s_adj = np.sqrt(p_adj**2 + q_adj**2)
            ^^
NameError: name 'np' is not defined
```

## Evidence
- Checked `src/besx/infrastructure/ui/streamlit/pages/step_rules.py`: `import numpy as np` is indeed missing from both top-level and `render_step_rules` function.
