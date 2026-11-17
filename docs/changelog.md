# Changelog

## 17 November 2026: mesh check with the hardening EP material (Q9)
- `make_decks.py --source … --kinds ep_miso` builds an EP deck from a refined SYS deck. The defaults are unchanged.
- The refined EP mesh is identical to the refined elastic mesh. New `plot_mesh_ep.py`.
- **5 mm → 2.5 mm with the Workbench EP material:** force −0.07 % to −0.28 %, peak plastic strain ×1.64.
- **The USERMAT on the same meshes:** force −7.7 % to −12.1 %, peak plastic strain ×2.77.
- The force mesh dependence comes from the JC-PINN softening. The load-patch concentration affects the local peak strain for both materials.
- Evidence: `bracket/ansys_usermat/mesh_ep_2026-11-17/`. Q9 stays open.

## 17 November 2026: bracket mesh study, the post-peak response is mesh dependent (Q9)
- New tools:
  - `refine_mesh.py` refines the Workbench mesh uniformly (2 × 2 × 2: hexes in parametric space, prisms as 15-node wedges). This replaced a Workbench remesh, because Workbench 2026 R1 is not on this machine.
  - `make_decks.py --source PATH --label NAME` builds elastic and USERMAT decks from any `ds.dat`. Its default and `--porosity` outputs are unchanged.
  - `plot_mesh.py` compares the meshes.
- **5 mm → 2.5 mm** (7,304 → 58,432 elements):
  - elastic stiffness −0.07 %;
  - peak reaction −7.7 %;
  - reaction after the peak up to −14.9 %;
  - max EQPS 0.36 → 0.99.

  The response after yield is mesh dependent. A regularised softening law would be needed. Q9 restated. Evidence: `bracket/ansys_usermat/mesh_2026-11-17/`.

## 17 November 2026: bracket porosity comparison (density only, one mesh)
- `make_decks.py --porosity` writes five USERMAT decks that differ only in TBDATA:
  - φ = 0, 4 and 7.85 % at G = 24541 MPa;
  - G = 23313.95 and 25300 MPa at φ = 4 %.

  Without the flag it writes byte-identical decks to before. New `expected_flow_stress.py` gives the single-element expectation and `plot_porosity.py` the plot and summary.
- **Bracket:** φ 0 → 7.85 % at fixed G lowers the peak reaction by 0.16 % (190.53 → 190.23 kN), the same as the single-element change near yield (−0.15 %). At −2 mm the drop is 0.34 %, which is post-peak and mesh dependent. G −5.0 % and +3.1 % move the peak by −1.76 % and +0.98 %.
- **Runs:** all converge with 0 errors, and phi4 repeats the earlier study-point run exactly.
- This is the density-only part of the porosity effect; G(φ) is still unknown (Q4). Evidence: `bracket/ansys_usermat/porosity_2026-11-17/`.

## 17 November 2026: bracket solved with the JC-PINN USERMAT (one mesh)
- New `bracket/ansys_usermat/`:
  - `make_decks.py` writes MAPDL decks from the committed Workbench `ds.dat` files without changing them. The decks are elastic, EP (MISO) and USERMAT at the study point. It rewrites the 2026 R1 `eblock,COMPACT` block so that MAPDL 2024 R1 can read it.
  - `post_bracket.mac` writes the per-substep histories, and `plot_results.py` plots them.
- On the Workbench mesh (7,304 SOLID186 elements) and its −2 mm imposed UX, the USERMAT run converges to the end with one bisection. The reaction peaks at 190.4 kN at −0.455 mm and is 136.7 kN at −2 mm. Peak element stress is 136 MPa, and peak EQPS is 0.36. 190 elements end beyond EQPS 0.0999.
- The elastic and EP decks repeat the original Workbench solves substep for substep.
- Evidence: `bracket/ansys_usermat/results_2026-11-17/`. Q9 is narrowed; mesh dependence is still open.

## 17 November 2026: verifier fix for NumPy 2
- `scripts/verify_jc_pinn.py` crashed under NumPy 2.5 because `predictions_reproduced` was a NumPy `bool_`, which `json` cannot write. `all_passed` also skipped it, because its filter only accepts Python `bool`. The check now compares the Python floats it already stores. On the locked run every check passes, with predictions reproduced to 2.6e-13. The locked run's files are unchanged.

## 17 November 2026: ANSYS single-element test passes
- The USERMAT was built and run in MAPDL 2024 R1 on the user's machine. ifx 2026.2 replaced the ifort 2023 that the UPF guide asks for, because that version is no longer downloadable. The single-element S11 matches `expected_single_element.csv` to 1.2×10⁻⁵ MPa at all 240 substeps. Final values: S11 = 75.41 MPa, EQPS = 0.1188, flag 1. The evidence is in `umat/ansys_test/results_2026-11-17/`. Q10 is closed.
- `single_element.mac` fixes: `OUTRES,SVAR,ALL`, so the state variables are saved, and `STORE,MERGE` before `*GET ... NSETS`, so the CSV gets all rows.
- `umat/README.md` now describes the v241 layout, where `usermat3d` lives inside `usermat.F`.
- The Fortran, the model, the expected curve and the tolerance are unchanged.

## 17 November 2026: user answers recorded
- The user confirmed the units, confirmed density as porosity, and declined data above 200 °C (decisions D1–D3). Q1, Q3 and Q6 are closed.
- The report, paper and slides still say "units inferred". Updating them needs a rebuild of the numbers and PDFs.

## 17 November 2026: ANSYS USERMAT
- New `umat/jc_pinn_usermat3d.F`, an ANSYS `usermat3d` wrapper around the same core as the UMAT. It returns plastic strain, `epseq`, energies and the consistent tangent, and sets `keycut` for bisection.
- The generator now builds both files from a shared core template plus one wrapper per solver. The Abaqus file was regenerated; its numbers are unchanged.
- `verify_umat.py` and `tests/test_umat.py` run every check through both wrappers. Not yet run inside ANSYS.

## 17 November 2026: Abaqus UMAT (post-hoc, model unchanged)
- New `umat/jc_pinn_umat.f`, generated by `scripts/write_umat.py` from the locked `equation.json`. It is a J2 radial return whose flow stress is the JC-PINN ensemble, with an analytic slope and a consistent tangent.
- New `scripts/verify_umat.py` and `tests/test_umat.py`. They compile the UMAT with gfortran and an offline driver. Agreement with the Python model is 2e-15 for stress and 1e-10 for the tangent, and results do not depend on increment size. The evidence is in `umat/verification.json`.
- Not yet run inside Abaqus.

## 9 November 2026: porosity analysis (post-hoc, descriptive)
- New script `scripts/porosity_analysis.py`, writing `reports/jc_pinn_20261107/porosity_analysis.json`.
- What it found:
  - lower density gives lower stress in all 72 density-only pairs;
  - φ 0 → 7.85 % lowers stress by 0.34 %, and the drop grows with temperature;
  - Equation 1's r fitted to 0, though the data imply ≈ 0.04, and the network reproduces the effect (correlation 0.97);
  - G acts about 16 times more strongly.
- New report section, paper paragraph, slide and figure (`fig_porosity`). The model is unchanged.

## 7–9 November 2026: final model release

**Model** (locked 7 Nov; unchanged since):
- JC-PINN: the user's Equation 1, multiplied by a 5–16–16–1 tanh correction that starts at zero. Five-copy ensemble.
- Training-only selection over 14 settings, a lock, then a single test: 0.439 MPa mean curve RMSE on 37 cases.
- Independent NumPy verifier; Colab/Kaggle notebook (PREDICT, FAST and FULL modes); fully explained notebook.

**Evidence:**
- Test report, with every one of the 37 cases.
- Post-hoc control with Equation 1 off.
- Improvement screen.
- Frozen baselines of the earlier MLPs.
- Errata for the λ = 0 extrapolation note.

**Media:**
- Narrated explainer video (3:02) and test-results video (3:00), with captions.
- Interactive model viewer, structure page and motion page.

**Documents:**
- Course report (15 pages) and IEEE-format paper (5 pages), sharing one bibliography. Every number comes from `report/numbers.tex`, which is generated from the run.
- 17-slide deck with speaker notes.
- Figures regenerated by `scripts/make_figures.py`.

**Repository:**
- Rewritten around the final model, with the old state archived on `archive/pre-final-2026-11-07`.
- The ANSYS project and CAD moved unchanged to `bracket/`.
- The porosity workflow and ANSYS bridge ported to the JC-PINN.
- New README and docs.

## 2 November 2026
Single MLP on the same split, with a Colab notebook. Now archived; its numbers are frozen in `baselines.json`.

## 24–31 October 2026
Five-network query MLP ensemble, Model Studio, porosity workflow, ANSYS project and the effective-equation study. Now archived.
