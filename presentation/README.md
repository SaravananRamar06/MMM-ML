# Corrected final presentation (use this one)

`Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx` and its PDF apply the 9 November 2026 audit
(branch `codex/presentation-audit`, commit `118fdf5`). Build: `build/build_corrected.js`. Corrections, evidence and
verification are in [`verification_corrected/README.md`](verification_corrected/README.md). The section below describes the
uncorrected original, kept unchanged for reference.

**Update of 17 November 2026 (now 24 slides).**
- The units wording now says the units were confirmed by the user (no generator documentation), and that density stands for porosity (also confirmed). The phrase "units inferred" no longer appears.
- Four slides were added after the evaluation, with speaker notes. Their numbers are read from `report/numbers.json`, and their figures come from `figures/`:
  - **17:** the locked model as an ANSYS/Abaqus user material, with the offline and MAPDL single-element checks;
  - **18:** the bracket with the JC-PINN and the density-only porosity comparison;
  - **19:** porosity with G coupled by the assumed G = 25300 (1 − φ) (decision D5);
  - **20:** the mesh study (the response after yield is mesh dependent).
- The deployment slide now shows the bracket coupling as existing but unvalidated, and Limits and the conclusion add the mesh dependence.
- Build: `NODE_PATH=<dir with node_modules/pptxgenjs> node presentation/build/build_corrected.js <pptx skill dir with scripts/apply_theme.js>`.
- PDF: `soffice --headless --convert-to pdf`.

**Submission deck (18 November 2026).** `scripts/make_submission_deck.py` writes `submission/Team8_Presentation_source.pptx`: cover, 15 content slides (2, 3, 5, 7, 9, 10, 12, 14, 15, 17–20, 22, 23 of the corrected deck, renumbered 1–15) and the thank-you slide. That file was imported into Canva and exported as `Team8_Presentation.pptx` / `.pdf`; the exports are part of the submission folders built by `scripts/build_submission.py` and are not committed.

`JC-PINN.pptx` (built by `scripts/build_deck.py` from `report/numbers.json`) got the same four topics and the units fix (21 slides).

---

# Final presentation (use this one)

`Final Presentation - Porosity in an AM Wing Bracket.pptx`: 20 slides, 16:9, speaker notes on every slide, plus a PDF copy.
The design uses a blueprint cover, navy/steel/orange colours, Arial headings with Calibri body text, and a life-cycle tracker on every
content slide. Built by `build/build_final.js`.

| # | Slide | Rests on |
|---|---|---|
| 1 | Title, team, course, instructor, college | Team roll numbers from the October deck; instructor Prof. Arul Kumar Mariyappan (course emails) |
| 2–4 | Problem, objective, life cycle | CL = critical flaw length; φ = 4 % assumed; K_IC source and porosity dependence still to be defined |
| 5 | CAD, loads and supports | `Rib Bracket.STEP` measured with gmsh; statics R = F, M = F × 210 mm; upper-half bore reasoning |
| 6–8 | Ansys: EL, elasto-plastic JC, user-defined JC | `source/Comparison Study - Final.wbpj` and the team's contours in `source/results/` (595.27 / 320.79 / 323.81 MPa), not independently re-run |
| 9–11 | EDA and data preparation | `source/model/` curves (all 73 cases) and `manifest.json`; one-level factor effects recomputed: T 22.1, rate 17.5, G 3.4, ρ 0.19 (units inferred as MPa) |
| 12 | Choosing the NN | Training-side scores: JC equation alone, one plain MLP, JC-PINN; switched-off control disclosed |
| 13 | JC-PINN versus a plain MLP | Test 0.143 / 0.439 / 0.338 / 7.37 and unseen-group means 11.90 / 6.24 / 5.63 / 13.95 |
| 14 | JC-PINN model | Architecture and the recorded training trace (GIF) from `reports/jc_pinn_20261107/` (branch `claude/tender-hamilton-vd2qvm`) |
| 15–16 | Evaluation | 37 cases held out from fitting, scored after locking; not a blind test. 0.44 mean RMSE, R² 0.9995, per-condition RMSE, test GIF |
| 17 | Deployment | Planned, not yet built; Model Studio still serves an earlier MLP |
| 18 | Limits and open questions | Evidence, unconfirmed definitions, porosity (r ≈ 0), and what CL still needs |
| 19–20 | Conclusion, Thank you / Any Questions? | |

Units: stress in the material data is inferred to be MPa (unconfirmed). The porosity levels 0 / 3 / 7.85 % are inferred from density
and await the professor's confirmation.

The two GIFs (`assets/gif_training.gif`, `assets/gif_test.gif`) animate in PowerPoint Slide Show. `build/data_figures.py` regenerates them,
the EDA figure and the cover background. It refits nothing.

---

# Earlier deck: Effect of Porosity on an AM Wing Rib Bracket

`Porosity in an AM Wing Rib Bracket.pptx` (15 slides, 16:9, speaker notes on every slide) and a PDF copy.
It replaces the October deck, which used a home-made Python solver, treated CL as lift in one version and
quoted unverified capacity-loss figures. None of that content is reused here.

| # | Slide | Rests on |
|---|---|---|
| 1 | Title | Team names and course |
| 2 | Problem statement | Laser powder-bed fusion porosity (general background) |
| 3 | Objective: CL(φ) | CL = critical flaw length (user, 27 Oct); φ = 4 % assumed (`configs/study_assumptions.json`) |
| 4 | Impact in service | Qualitative mechanics; the "about 2×" factor is the classical stress concentration for a round void |
| 5 | CAD model | `Rib Bracket.STEP` measured with gmsh: 231.5 × 230 × 40 mm, 778 cm³, Ø10 mm bore, two 50 × 40 mm mounting faces at x = 210 mm |
| 6 | Forces | Bore at x = 0, mounting faces at x = 210 mm, so R = F and M = F × 210 mm; arm tension/compression is a truss estimate |
| 7 | Why the upper half of the bore | The STEP bore is two 628 mm² half-faces; pin-bearing contact reasoning |
| 8 | Comparison Study set-up | `source/Comparison Study - Final.wbpj`: three Explicit Dynamics (AUTODYN) systems named Elastic, Built-in JC and User Defined JC, all using `Rib Bracket.STEP` |
| 9–11 | EL, JC-B, JC-U | Material property lists for AlSi10Mg - EL / JCB / JCU in the same `.wbpj` |
| 12 | Comparison | Capabilities of each material model, plus the results we expect |
| 13 | Results | Your Workbench contours (`source/results/`), equivalent stress at t = 0.06 s: EL 595.27, JC-B 320.79, JC-U 323.81 MPa |
| 14 | Results comparison | Same three peaks: EL = 1.85× JC-B; JC-U is within 0.94 % of JC-B; the EL peak sits at the fixed mounting-face corner and both JC peaks sit at the bore |
| 15 | Approach | JC-PINN test result (0.44 MPa mean curve RMSE, R² = 0.9995, 37 cases) from `reports/jc_pinn_20261107/` on branch `claude/tender-hamilton-vd2qvm` |

## Not in the project file, so the deck does not state it

The `.wbpj` holds the project structure only. Material constants, load magnitude, end time, mesh and results
are in `Comparison Study - Final_files/`, which was not supplied. The results slides use your contour screenshots instead. Still open:

- **F has no magnitude.** Its direction (+Y, upper half of the bore) follows the stated load choice. The fixed support on both mounting faces matches the earlier `Elastic.wbpj`; check it against the Comparison Study set-up.
- **Slide 11 says the JC-U table comes from the user's customised JC law (Equation 1).** The `.wbpj` only shows that JC-U uses a multilinear isotropic hardening table, so confirm the source.

## Rebuild

```bash
pip install gmsh==4.15.2 matplotlib numpy pillow      # gmsh needs libGLU on Linux
python presentation/build/extract_planform.py presentation/build/planform.json
python presentation/build/diagrams.py presentation/build/planform.json
python presentation/build/crop_results.py
python presentation/build/data_figures.py presentation/build/planform.json
NODE_PATH=<dir containing pptxgenjs> node presentation/build/build_final.js <pptx skill dir>   # final deck
NODE_PATH=<dir containing pptxgenjs> node presentation/build/build_deck.js <pptx skill dir>    # earlier deck
```

Fonts: Calibri throughout, plus Carlito (metric-compatible with Calibri) inside the diagram images. Colours: navy `14213D`, steel `2F5D8A`, signal orange `E8590C` for loads and porosity.
