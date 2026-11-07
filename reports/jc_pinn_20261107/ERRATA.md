# Errata for the locked run `jc_pinn_20261107`

The files below are part of the locked run. `equation.json` is fingerprinted in `selection_lock.json`, and `results.json` is the record of that run. They are left byte-for-byte unchanged, so that the lock and the evidence trail stay verifiable. The corrections are recorded here instead.

| File | Field | Recorded text | Correct reading |
|---|---|---|---|
| `equation.json` | `validity.note` | "200-300 C follows Equation 1 through the physics term only and is unvalidated." | The selected model has λ_phys = 0, so no physics term acts anywhere. Between 200 and 300 °C nothing constrains the prediction except the Equation 1 backbone and the smooth network. Those curves are unvalidated extrapolation. |
| `results.json` | `study_point.note` | "300 C has no data: its curve follows Equation 1 through the physics term only and is unvalidated." | As above: 300 °C curves are unconstrained, unvalidated extrapolation. |

The wording was written before the selection chose λ_phys = 0. The current `src/jc_pinn.py` writes the correct note for future runs (`extrapolation_note`). No prediction, metric or weight is affected.

**Code version:** the run was produced by `src/jc_pinn.py` at commit `c3ee1a6`, whose SHA-256 begins `d3f66db6`, as recorded in `selection_lock.json` and `results.json`. Later commits changed plotting, wording and reporting helpers only.
