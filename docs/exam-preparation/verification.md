# Preparation-pack verification, 17 November 2026

## Scope and preservation

This turn adds teaching material, a printable builder and an offline practice page. It does not retrain/reselect the submitted model, run a new bracket simulation or change a saved scientific result. Initial Git status was clean. Raw instructor data, environments and scratch QA files remain excluded. The original deck, paper and report are unchanged.

The numerical placeholders in the three teaching sources are resolved from `report/numbers.json`. Worked examples explicitly labelled illustrative are calculations for teaching, not new project observations. General materials/mechanics explanations are separated from project-specific evidence. The evidence map and primary/official background references are in the pack index.

## Checks performed

- Installed `requirements.txt` and `requirements-dev.txt` in the local virtual environment. Optional PDF-generation tools were also installed locally; the committed optional dependency file only requires reportlab.
- `python -m pytest -q`: **28 passed, 1 skipped, 8 failed; 30 subtests passed**. All eight failures are execution failures in the compiled Fortran-driver tests in `tests/test_umat.py`, for the two solver wrappers. A retry with broader execution permissions still returned **WinError 4551: An Application Control policy has blocked this file**. No application-control setting was changed or bypassed. This turn therefore does not claim a clean full-suite pass or freshly reproduced Fortran numerical checks. The existing saved Fortran/ANSYS evidence remains the source for those results.
- `python scripts/verify_jc_pinn.py reports/jc_pinn_20261107`: **all checks passed**, including lock hash/order, split isolation, saved metrics and prediction reproduction. Maximum JC-PINN prediction difference: 2.5579538487363607e-13 MPa.
- `python scripts/test_report_jc_pinn.py`: completed successfully without fitting. Recomputed test mean curve RMSE: 0.4386287734712186 MPa. A recursive comparison against the committed JSON outputs found a maximum numeric difference of 1.4210854715202004e-14, attributable to floating-point evaluation in the current environment. Figures were also regenerated with the local plotting stack.
- Restored only those check-generated changes in `reports/` to their pre-turn committed bytes after comparison. `git diff --stat reports/` is empty. Thus no saved result changed and no report-number/figure/deck/PDF scientific rebuild is needed.
- `python scripts/build_study_pack.py`: generated four printable PDFs, three resolved Markdown guides and 42 offline viva cards. The complete pack is 25 pages; the individual handbook, viva and workbook are 10, 8 and 5 pages. The combined version also includes the evidence/reference index.
- Rendered every combined-PDF page with Poppler and reviewed the page montage; inspected updated pages and the final first page at larger size. Extracted PDF text; all content bounding boxes remain inside their pages, and the generated teaching guides contain no unresolved result placeholders.
- Exercised the offline quiz script in a Node VM with a minimal DOM: all 42 cards load; reveal/hide, rating, previous/next, topic filtering, shuffle and reset work. This is function-level verification, not a full browser end-to-end test. Ratings are explicitly session-local and no network or upload is used.
- `git diff --check`: clean before commit.

## Reproduction notes

Use the repository's Windows Python environment with `requirements-study.txt` to rebuild the learning artifacts. The PDF builder uses Windows Arial fonts. PDF rendering/QA tools are optional verification dependencies, not needed to read the outputs. The source and generated material are committed so readers do not need Python to study.

No notebooks were re-executed: the task changes teaching documentation and its artifact builder, not the model/notebook implementation. No new hosted-Colab, Kaggle, ANSYS or Abaqus run is claimed. Full Fortran retesting remains limited by the machine's application-control policy.
