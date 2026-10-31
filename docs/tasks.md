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
- [x] Complete the factual course report, bibliography and corrected saved-diagnostic figure; compile the reviewed LaTeX source into a five-page PDF, inspect all pages and export identical copies in project files/. Evidence: report/build_verification.json.
- [ ] Research-paper version of the report, due **Wed 28 Oct 2026**: paper/paper.tex + refs.bib compiled (3-page IEEE draft, project files/Research Paper.pdf); ANSYS files expected 27 Oct morning; solver/units/porosity remain open limitations.
- [ ] Confirm the professor’s final submission template and complete submission-specific review after that information is supplied.
- [ ] Confirm submission format, exact deadline and whether the tentative model-count limit includes an ensemble or GP reference.

## Scientific work still open

- [ ] Planned 31 October: fresh beginner Colab notebook, scikit-learn, one query
  MLP and E11-to-Svm prediction using the preserved case split; no implementation
  requested in the planning discussion. Future porosity-input guidance is
  documented in porosity-workflow.md. Use fixed nominal phi=0.04 as the user's
  study assumption in metadata; source-history applicability and material
  mappings remain pending.
- [ ] Confirm the generating solver/material law, loading setup, output averaging, units and strain/stress definitions.
- [ ] Establish whether density/modulus levels encode porosity, and justify any mapping before using it.
- [ ] Obtain aerodynamic labels or an agreed physical calculation for coefficient of lift, C_L.
- [ ] Define the material/porosity-to-structure-to-aerodynamics coupling.
- [ ] Inspect actual teammate ANSYS files, boundary conditions, material inputs and solved results.
- [ ] Validate any material transfer or multiscale prediction before claiming it is complete.
- [ ] Obtain independent experimental or new simulation evidence for stronger generalisation claims.

The current model predicts supplied material responses. Missing lift labels and unresolved physical coupling prevent an evidence-backed porosity-to-lift claim. These open definitions do not prevent using the existing predictor with its documented limits.

- [x] 26 October Windows checkout: clone, review current model, verify bundled predictions, run 17 unit / 3 live checks, exercise browser and CLI, and provide Windows usage instructions. Fresh raw-data audit/refit remains unavailable until professor-supplied data is restored.

- [x] Fresh audit of restored professor data: 73 histories / 2,197,000 finite rows, source hashes, target reconstruction and training-only scalers verified.
- [ ] Explain/isolate frozen-settings Windows training difference before claiming exact training portability.
- [ ] Confirm physical porosity mapping and material-law definitions; generate validated bracket and aerodynamic labels before claiming porosity-to-C_L capability.

- [x] Implement and test conditional material-porosity studies, solver CSV comparison, CL calculation from actual aerodynamic inputs, CLI and browser interface.
- [x] Import STEP solids with CAD kernel, measure volumes and identify face tags for a future verified FEA setup.
- [ ] Obtain confirmed physical inputs and solver model, run/validate structural and aerodynamic analyses, and only then train/evaluate any new bracket/lift predictor. Full requested physical model remains incomplete.
