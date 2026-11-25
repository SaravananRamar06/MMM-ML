# Changelog

## 25 November 2026: project flowcharts show the critical flaw length as done
- `docs/project-flowchart/project.dot` and `simple.dot` still drew step 5 (CL) dashed as "not done yet". Step 5 now reads as assessed post-hoc on 20 Nov (decisions F1, F2): 2D fillet crack, K_I by FE, BS 7910 failure assessment, CL > 30 mm at the 35.9 kN capability-based limit load, at every porosity, for K_mat 36–50 MPa√m; a bound, not a value; static, not fatigue. Drawn solid like the other steps. Both limits notes add that 35.9 kN is a capability bound, not a service load. The numbers are those of `report/numbers.json` (`ClLimitkN`, `ClCrackMin`, `ClCrackMax`, `ClKmatLow`, `ClKmatHigh`).
- `build.cjs` now stops if the CL numbers in either `.dot` file no longer match `numbers.json`. PNG and SVG rebuilt (Graphviz 16.1.0 via `@viz-js/viz`; an unchanged rebuild reproduced the old files byte for byte). The folder README no longer says step 5 is planned.

## 25 November 2026: complete study guide for the end-semester examination
- **New:** `docs/exam-preparation/complete-study-guide.md` and its PDF `output/pdf/complete-study-guide.pdf` (61 pages). It covers the whole project in order, from the problem and data to the critical flaw length, with background theory marked as such, the decisions, limits and open questions, a formula sheet, key numbers, a glossary, 75 practice questions with model answers, 17 worked numerical problems and a list of common mistakes.
- **Sources:** every project number was read from `report/numbers.json`, the locked run, the bracket and crack result folders and `umat/`; the worked examples (Equation 1 at the study point, the shape ratio 0.476, the FAD weakest case, the limit load, μ, plastic-zone and a_c examples) were recomputed from `equation.json`, `equation_only.json` and `fad_cl.json`. Nothing in `reports/` or any saved result was changed, and the model is unchanged.
- **Build:** `scripts/build_study_guide.cjs` (pandoc to HTML with MathML, then Chromium print via Playwright for Node).
- **Pointers:** README and the exam-preparation README now point to the guide first.
- **Second check (same day, before merging):** `scripts/check_study_guide.py` cross-checks 234 quoted values against `numbers.json`, the locked run, the bracket and crack result folders (0 failures); the pooled test RMSE (0.504), R² and the Equation 1 shape ratio were recomputed from `test_predictions.csv`. A full reread found no wrong number but corrected the wording in 11 places. Examples: the 200 °C/10⁻⁵ cell holds 1 case, not 9. The 136.06 MPa initial yield applies to the study-point runs only. The 17 Nov LEFM estimate was an illustration, not a method that was used. The 2.5 mm first-yield location is unknown. The energy release rate is no longer written G.

## 22 November 2026: final check of the repository, the report and the paper
- **Checks run (no model or locked file changed):**
  - `pytest`: 33 passed, with the stand-in raw folder from `build_raw_from_committed_curves.py`;
  - `verify_jc_pinn.py`: every check passes, predictions reproduced to 2.6e-13;
  - `test_report_jc_pinn.py`: JSON, CSV and README unchanged (its three PNGs differ only in bytes on this Matplotlib and were restored);
  - `verify_umat.py` (gfortran): passes and rewrites `umat/verification.json` unchanged;
  - `run_notebooks.py` on a copy of the repository: both notebooks run with 0 errors, and FAST mode reproduces the locked weights and constants exactly;
  - `fad_cl.py` and `check_limit_load.py`: every CL output and quoted limit-load value reproduces; `validate_2d.py` gives the same values;
  - `write_latex_numbers.py`: all 172 earlier macros unchanged. The hard-coded numbers in the report, paper and deck (data counts and ranges, the condition table, the selection table, r = −0.027 without the bound, 2579 points, the EP yield, the stiffness ratio, the deck's EDA and geometry numbers) were recomputed and agree.
- **Report (21 → 24 pages):** the 20 Nov critical-flaw-length assessment was missing, and the limitations still said CL was not predicted. New section "Critical flaw length" (load and toughness, method, result, caveats), with 51 new macros read from `crack2d_2026-11-20/` and the limit-load inputs, the two CL charts (`fig_crack_residual`, `fig_crack_cl_load`, copied by `make_figures.py`) and two references (BS 7910:2019; 14 CFR Part 25). Abstract, introduction, limitations and conclusion updated. Corrections: "Two caveats apply" listed one (the second, the removed ensemble, went in C2); case 60 rises again after it collapses; the 14 settings are seven physics options × two constant modes; the report covers the bracket too; ANSYS was run at one temperature and rate, not one material condition; Fig. 7 is now referenced.
- **Paper (5 pages):** the abstract said five seeds were compared (selection used three; five is the final ensemble). New CL paragraph, limit and conclusion. The unreferenced test-RMSE bar chart (the same numbers as Table II) was removed, and two full-width figures were narrowed, to stay at 5 pages.
- **CL sensitivity added:** the 2D section's fillet tension per kN is 5.0 % below the 3D model's, which is not conservative for K_I. Scaling every K_I up by 5.2 % still leaves the weakest case at 43.3 kN, above 41.3 kN (`write_latex_numbers.py`, `ClKScaledWeakkN`).
- **Documentation fixes:**
  - `crack2d_2026-11-20/README.md`: 10 of the 15 residual-strength values were 0.01–0.035 kN off `residual_strength.csv`; the crack line leaves the section at about 39 mm (keypoint 31 of every `crack.dat`), not 33 mm (also in the limit-load note);
  - Q5: CL at K = 20 MPa√m is 23.4–23.5 mm at every porosity (was "about 23 mm, φ = 7.85 %"), and the 2D/3D fillet-tension caveat;
  - the limit-load note no longer says the FAD run is uncommitted; `decisions.md` no longer links the deleted `history.md`; `umat/README.md` and the ANSYS flowchart README no longer say CL is not predicted; README and `report/README.md` page counts.
- **Slides:** the 24-slide deck (`build_corrected.js`) still showed CL as planned and the model-to-ANSYS coupling as proposed. Slides 1, 3, 4, 8, 21, 22 and 23 now state what exists, with CL numbers from `numbers.json`; slide 15 quotes ±1 MPa; two speaker notes no longer say "lowers … by −x %". Rebuilt and exported with LibreOffice (Carlito / Liberation Sans). Still 24 slides.
- **Exam preparation pack:** the CL answers (handbook §10, viva Q40 and drill E, workbook K, mock Q6, slide notes), viva Q37 and mock Q5 (built on the superseded −X mesh result) and the evidence map were updated, and the resolved Markdown and practice page regenerated. Its five PDFs need Windows fonts and still date from 18 Nov; rebuild them on Windows.
- **Submission builder:** ships `crack2d_2026-11-20/`, the crack scripts and `check_limit_load.py`, and describes the CL result instead of "no critical flaw length".

## 21 November 2026: 17-slide presentation guide
- `presentation/17-slide-authoring-guide.md`: the Canva authoring guide for the team's 17-slide presentation (cover, 15 content slides, questions), with the critical flaw length on slides 15–16. New slide graphics in `presentation/assets/`: the porosity-study workflow (with and without captions), the model-selection workflow and the bracket boundary-condition illustration.

## 20 November 2026: critical flaw length (decisions F1, F2)
- **Decisions (user):** K_mat is the literature band 36, 40 and 50 MPa√m at every porosity (F1); CL is assessed at the capability-based limit pin load of 35.9 kN as a damage-tolerance residual-strength check, with 41.3 kN (× 1.15 fitting factor) as a sensitivity (F2).
- **Model and runs** (`bracket/ansys_usermat/crack2d/`, `crack2d_2026-11-20/`): 2D plane-strain section with a through-thickness edge crack at the R10 fillet (a = 1–30 mm), K_I by interaction integral, collapse loads from JC-PINN USERMAT runs at φ = 0 / 4 / 7.85 % (G coupled, D5), BS 7910 Option 1 failure assessment diagram.
- **Result:** at 35.9 kN no modelled crack fails at any porosity or K_mat, so CL > 30 mm; the weakest case (30 mm, φ = 7.85 %, K_mat = 36) carries 44.80 kN. Porosity lowers the limit load by 2.3 % and the residual strength at 30 mm by 2.0 %. Q5 restated.
- **Limit-load check (PR #13):** `scripts/check_limit_load.py` and `docs/proposals/limit-load-check-2026-11-20.md`: 35.92 kN on the 5 mm mesh, about 28.5 kN on the 2.5 mm mesh, and P_L(φ) = 36.25 / 35.82 / 35.43 kN.
- **Project flowcharts (PR #12):** `docs/project-flowchart/`, in the team's order of work.

## 18 November 2026: contours, zone results and the ANSYS workflow flowchart
- `bracket/ansys_usermat/contours_uy_2026-11-18/`: MAPDL contour pictures of the corrected-load runs. `zones_uy_2026-11-18/`: zone-by-zone stresses and plastic strain (`zones.json`), which give the 3.788 MPa/kN fillet stress used for the limit load.
- `docs/ansys-flowchart/`: the ANSYS, USERMAT, JC-PINN and return-mapping flowcharts.

## 18 November 2026: bracket load corrected to the pin load +P_y on the upper half of the bore
- **Decision (user, from the load figure):** the pin load is +P_y (wing-normal upload) and bears only on the half of the bore that faces it. Every bracket run used the Workbench file's load, UX = -2 mm on the whole bore; that is superseded.
- **Tools:** `make_decks.py --load plus_y` imposes UY = +2 mm on the bore nodes with y >= 0 (the STEP splits the bore at y = 0). `post_bracket.mac` writes the displacement and reaction along the load axis; `history.py` reads both formats; the plot scripts reproduce all 236 values of the 17 Nov summaries unchanged. `extract_key_lines.py` writes the solver-log evidence.
- **Re-run (14 MAPDL runs, 0 errors):** `results_`, `porosity_`, `porosity_gphi_`, `mesh_`, `mesh_ep_uy_2026-11-18/`. Under +P_y the bracket bends: stiffness 140.8 kN/mm elastic, 120.0 kN/mm USERMAT (ratio 0.852 as before). The USERMAT peaks at 100.5 kN at UY = 1.150 mm and softens to 86.3 kN at 2 mm. Density only changes the peak by -0.17 %; with G coupled (D5) by -3.38 % (-5.12 % at 2 mm). Halving the elements changes the peak by -9.8 % against at most 0.7 % for EP; the meshes no longer meet at 2 mm (-10.3 %). EP peak strain is at the R10 crotch fillet, USERMAT peak strain at the loaded half of the bore.
- **Workbench 2024 R1 project** re-solved with the upper bore half-face moved UY = +2 mm: peak 102.9 kN at 1.22 mm (batch 100.5 kN; different, swept mesh). The -X version's results stay in `workbench_2024R1/results_2026-11-18/`.
- **Numbers and documents:** 42 values in `numbers.json` changed (`BrUsermatPeakUX`, `MeshPeakFineUX` renamed to `...PeakU`); report (21 pages), paper (5 pages), the corrected deck and its 17-slide submission source, README, open questions and the study pack were updated, and claims that no longer hold were rewritten. The Canva deck (DAHbM5NbDYE) slides 11-16 were updated in Canva (text, four plots, speaker notes; slide 11's notes no longer mention Abaqus).
- **Submission:** `build_submission.py` builds the +Y decks and ships the +Y results, with the -X runs under `04_Results/superseded_load_minus_x/`.

## 18 November 2026: the USERMAT bracket as a Workbench 2024 R1 project
- **Why:** the USERMAT runs were MAPDL batch decks, so there was no Workbench file to open. The team's `Elastic.wbpj` is 2026 R1, and the USERMAT DLL is built for 2024 R1.
- **New:** `bracket/ansys_usermat/workbench_2024R1/` builds, meshes and solves `Bracket_USERMAT_2024R1.wbpj` in batch (`build_project.bat` runs `build_project.wbjn` and `mech_setup.py`). It has the team model's supports and load, a swept 5 mm SOLID186 mesh and the `TB,USER` block as a command snippet. `open_project.bat` opens it with `ANS_USER_PATH` set. The result file is not committed.
- **Result (post-hoc re-run, `results_2026-11-18/`):** peak reaction 190.0 kN at UX = -0.455 mm, against 190.4 kN in the batch deck (0.2 %); 134.0 kN against 136.7 kN at -2 mm (2.0 %; the meshes differ and the response after yield is mesh dependent). Contour pictures are exported.
- **Study handbook:** the removed ensemble baseline (`EnsTest`) is dropped. The study PDFs were rebuilt after the ANSYS-only clean-up and no longer mention Abaqus or `JC-PINN.pptx`.
- **Submission:** `build_submission.py` adds the Workbench 2024 R1 project (without solver scratch) and its results.
- **Submission rebuilt** from commit `1772ea1` (this branch: main 92f472d plus the study-PDF fix and the Workbench project), without Abaqus: no file name or text file in either upload or in `submission files/` mentions Abaqus or `jc_pinn_umat`. The Canva deck was re-exported after slide 11 was fixed (stat card: 2e-15 offline relative error; ANSYS USERMAT only); slide 11's speaker notes were rewritten in the exported PPTX, because the Canva tool cannot edit notes (the Canva design keeps the old notes). 17 slides with notes on every slide; every number on the slides and in the notes was checked against `report/numbers.json`, with no mismatch. Report: 21 pages, team names on the title page.

## 18 November 2026: Team 8 end-semester submission
- **Report:** a title page with the course, Team 8's names and roll numbers, the instructor and IIITDM Kancheepuram (21 pages).
- **Submission deck:** `scripts/make_submission_deck.py` keeps the cover, 15 content slides and the thank-you slide of the 24-slide corrected deck, renumbers them and fixes the cached slide numbers. It was imported into Canva, where the cover's team names were set to one size, and exported as `Team8_Presentation.pptx` / `.pdf` (17 slides, speaker notes on all of them). Every decimal number on the slides and notes was checked against `report/numbers.json`: no mismatch. The values not in `numbers.json` come from the team's Ansys screenshots (595.27, 320.79, 323.81 MPa and their ratio 1.86), the training trace (0.171 to 0.0028), the test summary (0.4386 = 0.439 unrounded; pooled point RMSE 0.504), 6.23 (`SelGroups` 6.235 rounded) and the 2.5 mm mesh size.
- **`scripts/build_submission.py`:** builds, from a `git archive` of one commit, `Upload_1_UMAT_UPF_and_FE_model/` (+ zip), `Upload_2_PPT_and_Report/` and `submission files/` (report, presentation, FEA simulations including the team's JC comparison study, USERMAT/UMAT code, the locked model weights and the Colab notebooks), each with a `MANIFEST.txt` (size, SHA-256, commit). Raw data, solver scratch files, the USERMAT DLL, environments and credentials are left out. The LaTeX source zip is test-compiled on its own (21 pages, no undefined references). The output folders are not committed.

## 17 November 2026: repository clean-up (decisions C1–C3)
- **Abaqus removed:** `umat/jc_pinn_umat.f`, `umat/templates/abaqus_umat.f.in`, `umat/test/ABA_PARAM.INC` and the Abaqus paths in the generator, verifier, driver and tests. The ANSYS USERMAT is regenerated with comment-only changes; its compiled code is identical to the one tested in MAPDL.
- **Earlier models trimmed:** `docs/history.md` and `scripts/freeze_baselines.py` removed. The five-network ensemble is gone from the README, docs, report, paper and the comparison figure (`fig_comparison`), and its macros (`EnsTest`, `EnsGroups`, `WinsEnsemble`) are dropped. The 2 Nov plain MLP stays as the one baseline. Files under `reports/` are unchanged, because the locked run is evidence.
- **One slide deck:** `JC-PINN.pptx/.pdf`, `scripts/build_deck.py`, the uncorrected final deck, the October deck, `build_final.js` and `build_deck.js` removed. The corrected deck is rebuilt without Abaqus or Model Studio mentions.
- After merging the submission work: `scripts/build_submission.py` no longer packages an Abaqus folder (the offline test driver moves into `01_USERMAT_ANSYS_UPF/verification/`); the study pack's Markdown and HTML no longer mention Abaqus or `JC-PINN.pptx`. Its PDFs in `output/pdf/` need Windows fonts, so rebuild them on Windows with `python scripts/build_study_pack.py` and `python scripts/build_study_textbook.py`.
- Report (21 pages), paper (5 pages), the corrected deck (24 slides) and the submission source deck (17 slides) rebuilt.

## 17 November 2026: open items (D4, D5, the coupled porosity study, Q5 reasoning)
- **D4:** Abaqus is not used. Q9 no longer asks for Abaqus runs. The hosted-notebook checklist (`docs/hosted-notebook-check.md`) is ready for the user to run for Q8.
- **Proposal:** `docs/proposals/open-items-2026-11-17.md` compares five G(φ) relations and an LEFM method for critical flaw length, with cited K_IC and Y values.
- **D5 (user):** G(φ) = 25300 · (1 − φ), the linear upper bound that the data's G levels follow exactly. It is written into `bracket/workflow/config.json` (status `assumed`).
- **Coupled study:** `make_decks.py --porosity-gphi`, `expected_flow_stress.py --gphi` and `plot_porosity_gphi.py`. Over φ 0 → 7.85 % with G coupled, the bracket changes by −7.85 % in stiffness, −2.86 % in peak force and −6.04 % in force at −2 mm, against −0.16 % / −0.34 % for density alone (`bracket/ansys_usermat/porosity_gphi_2026-11-17/`). Q4 is restated: the remaining question is a measured G(φ) to replace the upper bound.
- **Q5 stays open:** there is no service load, and LEFM is not valid at the yielding peak. The reasoning and the K_IC table are in Q5 and in the report's limitations.

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
