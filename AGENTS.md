# Instructions for agents working on this repository

This repository holds one model, the **JC-PINN** of 7 November 2026, and everything about it. Read [README.md](README.md), then [docs/decisions.md](docs/decisions.md) and [docs/open-questions.md](docs/open-questions.md), before changing anything.

## User rule: commit all project work to GitHub

Commit and push code, tests, documentation, research decisions and relevant verification evidence before ending each work turn. Use focused commits and verify that origin contains them. Respect the existing exclusions for raw data, credentials, environments, downloads and scratch files. Preserve uncommitted work that does not belong to the current task. Report the pushed commit IDs.

## Rules for this project

- **The locked run is evidence. Do not edit it.** `reports/jc_pinn_20261107/equation.json` is fingerprinted in `selection_lock.json`. Record corrections in `ERRATA.md`, and put new results in new files or folders.
- **The model is final.** The user decided to submit it as locked (decision A3). Do not retrain, re-select or tune on the 37 test cases. Any new experiment goes on training cases only and is labelled as post-hoc.
- **Numbers come from files.** The report, paper and slides read `report/numbers.tex` / `numbers.json`, which `scripts/write_latex_numbers.py` writes. After any change to a saved result, rerun it, then `scripts/make_figures.py` and `presentation/build/build_corrected.js` (the only slide deck), and rebuild the PDFs.
- **Do not ask again about resolved facts.** CL is critical flaw length. The data folder is complete. The split is 36/37 by case. The study point is φ = 4 %. Equation 1 and its constants are as in the user's notes. The units are °C, s⁻¹, MPa and kg/m³ (user-confirmed). Density stands for porosity. No data above 200 °C will be added.
- **State the limits.** The test is not blind, the units are user-confirmed (no generator documentation), nothing is validated above 200 °C, and nothing here is experimentally validated. Do not invent loads, porosity relations or fracture data.
- **Raw data stay out of Git.** `TEAM_8_extracted_results_set_1/` is the instructor's data and is excluded by `.gitignore`.
- **Earlier work lives on branch `archive/pre-final-2026-11-07`.** Do not restore it to `main`. The only earlier model quoted on `main` is the 2 Nov plain MLP, as a baseline.
- **ANSYS is the only finite-element solver.** The user material is the ANSYS USERMAT in `umat/`. There is no Abaqus UMAT; do not add one.

## Checks before pushing

Install `requirements.txt` and `requirements-dev.txt`. To re-execute the notebooks, run `python scripts/run_notebooks.py`.

```bash
python -m pytest -q
python scripts/verify_jc_pinn.py reports/jc_pinn_20261107
python scripts/test_report_jc_pinn.py   # rewrites test_report/
git diff --stat reports/   # must show no change in numbers
```

The same commit rule for Cursor is in `.cursor/rules/commit-project-work.mdc`.
