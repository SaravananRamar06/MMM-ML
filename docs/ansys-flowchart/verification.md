# Flowchart verification

These diagrams document the current code. They do not add a material model, change the locked weights or establish physical validation.

## Code cross-check

Checked the editable graph nodes and branches against:

- `umat/templates/ansys_usermat3d.F.in`, lines 83–116: interface requirements, optional property 7, state at the start of the increment, cutback and material-error returns.
- The same wrapper, lines 118–133: returned plastic strain, energies, equivalent plastic strain and four history variables.
- `umat/templates/jc_pinn_core.f.in`, lines 53–119: tolerances, properties, elastic trial and initial flow evaluation.
- The same core, lines 123–187: one-time multiplier-bracket initialisation, retained bracket, maximum 50 local evaluations, safeguarded Newton update, final slope check, stress correction and tangent.
- The same core, `JCPFLW` (lines 210–247): temperature/rate/density/G flags, lower and upper strain extensions, zero derivative strictly outside the interval.
- The same core, `JCPSIG` (lines 255–340): member-specific constants, standardisation, two tanh layers, geometric averaging and analytic strain derivative.
- `src/jc_pinn.py`, `equation_predict`: the same five-member geometric ensemble.

The source model SHA-256, also checked by the independent model verifier, is:

```text
73cac41864e4599e1f4a2a0eb2ba163bd011340b990cc4ea4cebe53f79342c5c
```

View A's general ANSYS retry and minimum-substep behaviour is referenced to the official [automatic time-stepping theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/ans_thry/thy_tool6.html). Actual iteration/recovery controls remain analysis-dependent.

## Rendering and viewer

- All four Graphviz graphs rendered successfully as SVG and PNG using `@viz-js/viz` 3.25.0 and `sharp`.
- Graphviz emitted one non-ASCII width-fallback warning. All resulting SVG text was checked in the browser; no node text extended beyond its node's bounding box. No Graphviz error was reported.
- Visually inspected the diagram renders, including the loop arrowheads, labelled branches, error terminals and formulas. Equations use explicit member-index notation such as `e^(n_k)` rather than ambiguous superscript strings.
- Headless Edge / Playwright verified that all four tabs display their panels, zoom changes diagram width to 150%, and a 390-pixel viewport does not cause document-level horizontal overflow. Diagrams intentionally allow their own scrolling at narrow widths.
- No browser JavaScript errors occurred. Inline SVG element IDs are prefixed per view to avoid collisions.
- [viewer-check.json](viewer-check.json) records the browser results. Node counts include explanatory notes; edge counts exclude invisible layout constraints.

## Repository checks

- Installed/confirmed `requirements.txt` and `requirements-dev.txt` in the existing `.venv`.
- `python -m pytest -q`: **28 passed, 1 skipped, 8 failed**, with 30 passing subtests. The eight failures are the existing numerical UMAT/USERMAT tests: compiled drivers return Windows code `0xC0E90002` without numerical output. A retry outside the sandbox had the same outcome. The cause was not diagnosed or fixed in this documentation task; the fresh Fortran numerical checks therefore remain unsuccessful.
- `python scripts/verify_jc_pinn.py work/ansys-flowchart-checks/locked-run`: **all_passed = true**.
- `python scripts/test_report_jc_pinn.py work/ansys-flowchart-checks/locked-run`: **passed**; it asserts agreement with the locked test score.
- The two report-writing checks ran on a copy of the run's top-level JSON/CSV evidence under ignored `work/`, preserving concurrent work in the original report directory. No model fitting was performed.

Only `docs/ansys-flowchart/` belongs to this change. Other existing edits and generated study materials are outside its scope.
