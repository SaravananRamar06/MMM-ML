# Changelog

## 17 November 2026: repository clean-up (decisions C1–C3)
- **Abaqus removed:** `umat/jc_pinn_umat.f`, `umat/templates/abaqus_umat.f.in`, `umat/test/ABA_PARAM.INC` and the Abaqus paths in the generator, verifier, driver and tests. The ANSYS USERMAT is regenerated with comment-only changes; its compiled code is identical to the one tested in MAPDL.
- **Earlier models trimmed:** `docs/history.md` and `scripts/freeze_baselines.py` removed. The five-network ensemble is gone from the README, docs, report, paper and the comparison figure (`fig_comparison`), and its macros (`EnsTest`, `EnsGroups`, `WinsEnsemble`) are dropped. The 2 Nov plain MLP stays as the one baseline. Files under `reports/` are unchanged, because the locked run is evidence.
- **One slide deck:** `JC-PINN.pptx/.pdf`, `scripts/build_deck.py`, the uncorrected final deck, the October deck, `build_final.js` and `build_deck.js` removed. The corrected deck is rebuilt without Abaqus or Model Studio mentions.
- Report, paper and deck PDFs rebuilt.

## 17 November 2026: report, paper and slides brought up to date
- **`write_latex_numbers.py`:** now also reads `umat/verification.json`, the MAPDL single-element CSVs and the bracket summaries (results, porosity, mesh, mesh_ep). It writes 60 new macros (164 in total). All 104 existing macros keep exactly the same values. `numbers.tex` and `numbers.json` are written with LF.
- **`make_figures.py`:** copies the four committed bracket plots into `figures/` (`fig_bracket*`, `fig_mesh*`) without redrawing them. The existing figures were left as committed, because the data are unchanged and re-rendering with this machine's Matplotlib only changed their bytes.
- **Report (19 pages):**
  - new sections "From model to finite-element material" (USERMAT, offline verification, MAPDL single element) and "Bracket results" (three materials, density-only porosity, mesh study);
  - updated abstract, limitations and conclusion;
  - wording for the units confirmed by the user, density as porosity, and no data above 200 °C (D1–D3).
- **Paper (5 pages):** a new section and figure for the finite-element material and bracket, plus an updated abstract, limits and conclusion. Other text was condensed to stay within 5 pages, and no limit was dropped.
- **Slides:**
  - `JC-PINN.pptx`: 17 → 20 slides (this deck was later removed, decision C3);
  - the corrected final deck: 20 → 23 slides, built with `build_corrected.js`. Its new slides read `numbers.json`, and its deployment slide now shows the USERMAT coupling as existing but unvalidated;
  - both decks have the three new topics with speaker notes, and "units inferred" is gone. Both PDFs were exported with LibreOffice.
- Q9's "what would close it" no longer lists the hardening-material run, which has been done.

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

## 17 November 2026: ANSYS USERMAT (post-hoc, model unchanged)
- New `umat/jc_pinn_usermat3d.F`, an ANSYS `usermat3d` generated by `scripts/write_umat.py` from the locked `equation.json`. It is a J2 radial return whose flow stress is the JC-PINN ensemble, with an analytic slope and a consistent tangent. It returns plastic strain, `epseq`, energies and the tangent, and sets `keycut` for bisection.
- New `scripts/verify_umat.py` and `tests/test_umat.py`. They compile it with gfortran and an offline driver. Agreement with the Python model is 2e-15 for stress and 1e-10 for the tangent, and results do not depend on increment size. The evidence is in `umat/verification.json`.

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
- Frozen baseline numbers of the 2 Nov plain MLP.
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

## Before 7 November 2026
Earlier models and materials, archived on branch `archive/pre-final-2026-11-07`. The 2 Nov plain MLP is kept as the baseline; its numbers are frozen in `baselines.json`.
