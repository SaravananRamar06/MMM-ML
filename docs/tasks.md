# MMM-ML task tracker

Updated 25 October 2026. Checkboxes reflect work supported by local artifacts. This current summary replaces older mixed model/app task lists; dated history remains in `logs.md`. The collaboration app is managed separately in AI-GroupChat.

## Completed material-model work

- [x] Inventory the professor-supplied data: 108 planned cases, 73 available histories, 2,197,000 rows.
- [x] Audit finite values, strain progression, common support, stress-component consistency and case-60 irregularity.
- [x] Save source hashes, a case manifest and equal-length 120-point curve caches.
- [x] Preserve the seed-42 split of 36 training / 37 test simulation cases.
- [x] Fit preprocessing on training cases and keep each simulation intact across partitions.
- [x] Complete compact-query and PCA-coefficient neural-network comparisons, GP reference and saved case/condition diagnostics.
- [x] Select and save the Svm query MLP ensemble: five 5–16–16–1 tanh networks, alpha 0.001.
- [x] Save test predictions, per-case errors and final model artifacts.
- [x] Provide equivalent NumPy inference and integrate it into Model Studio with joblib fallback.
- [x] Provide local Studio parsing, comparisons, point queries, tables and warnings.
- [x] Prepare the 24-slide presentation and detailed reference-guide files in `project files/`.
- [x] Update local and publication README sources in team voice without contribution credits.
- [x] Write a simple first-person model guide and fresh results document.
- [x] Rerun the full source audit, saved-model scoring and separate frozen-settings fit; protect original artifacts by hashes.
- [x] Rerun 13 unit and 3 live Studio checks successfully; leave Studio serving locally on port 8766.
- [x] Share fresh evidence and documentation handoff in the group chat.

Latest evidence: `reports/retests/20261025T172218Z/`. Mean test curve RMSE 0.05908515; worst 0.11330618 (case 45). Exact same-environment weight/prediction reproduction. Earlier all-data exploration and unconfirmed units remain disclosed.

## Publication and document review

- [x] Publish and fetch back the GitHub README in team voice, without contribution credits; publish the new guide, results, scripts, logs and SVG plot. Final document-index commit: be58a301b1b2dc607609fdd8143bbf2c799f6fa8; README commit: b2d90a390a2c0f222e5ea806f5ed2b2e2ed49d6b.
- [ ] Finish the full course report and final submission review. Existing guides and presentation do not establish that the formal report is complete.
- [ ] Confirm submission format, exact deadline and whether the tentative model-count limit includes an ensemble or GP reference.

## Scientific work still open

- [ ] Confirm the generating solver/material law, loading setup, output averaging, units and strain/stress definitions.
- [ ] Establish whether density/modulus levels encode porosity, and justify any mapping before using it.
- [ ] Obtain aerodynamic labels or an agreed physical calculation for coefficient of lift, C_L.
- [ ] Define the material/porosity-to-structure-to-aerodynamics coupling.
- [ ] Inspect actual teammate ANSYS files, boundary conditions, material inputs and solved results.
- [ ] Validate any material transfer or multiscale prediction before claiming it is complete.
- [ ] Obtain independent experimental or new simulation evidence for stronger generalisation claims.

The current model predicts supplied material responses. Missing lift labels and unresolved physical coupling prevent an evidence-backed porosity-to-lift claim. These open definitions do not prevent using the existing predictor with its documented limits.
