# Course report source and build

`report.tex` is the reviewed LaTeX source. `report.pdf` is the five-page compiled report. Final copies are in `../project files/Final Course Report.pdf` and `../project files/report.pdf`.

Build with Tectonic 0.17.0 from this directory:

```bash
tectonic --keep-logs --keep-intermediates report.tex
```

The first build fetches the required TeX packages; later builds reuse the local cache. Obtain Tectonic from its official project releases. No compiler binary is included in this repository.

Figures are resolved from `figures/` and `../reports/retests/20261025T172218Z/`. The condition chart is generated from saved diagnostics by `../reports/plot_report_diagnostics.py`, without refitting. Keep those paths when building from a clone.

`build_verification.json` records the approved source/PDF hashes and rendering checks. The factual review is in `../reports/final_report_fact_check_20261025.md`. The report documents unconfirmed units, earlier holdout exposure and missing porosity/lift/ANSYS validation. It is the completed current-evidence report; submission-specific requirements still need professor confirmation.
