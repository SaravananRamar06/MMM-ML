# Scientific audit and textbook publication

17 November 2026. This follow-up reviewed the preparation pack against the implementation and saved evidence, then published a textbook edition using ReportLab and Matplotlib MathText. It does not independently validate the simulated material or bracket.

## Corrections

1. **Range flags:** `umat/templates/jc_pinn_core.f.in`, routine JCPFLW, uses bit 2 for temperature outside 30-300 degrees C, or rate/density/G outside their data ranges. Bit 4 separately marks the unobserved 200-300 band. Thus 250 degrees C alone gives flag 4, not 6. The prior guide's generic wording "out-of-data condition" for bit 2 was imprecise and is corrected explicitly.
2. **Conflicting node counts:** removed the unsupported claim that the different counts in existing summaries arise from different node-set conventions. The summaries do conflict; an explanation requires deck-level investigation. No invented reconciliation is taught.
3. **Signed changes:** replaced wording equivalent to "falls -7.7%" with a signed-change statement, in the handbook and viva bank.
4. **Flaw length:** made the explicit critical-size expression conditional on constant Y. When the geometry factor depends on crack size, solve using Y(a_c). This qualification now appears in the handbook, viva and workbook.

## Checks and conclusions

- Compared backbone, scaling, architecture, parameter count, geometric ensemble, data loss, regularisation and selected lambda with `src/jc_pinn.py`, the configuration and locked run. The central description agrees. The trend residual uses derivatives in standardised condition coordinates; the selected lambda remains zero.
- Checked the local J2 return residual against `umat/templates/jc_pinn_core.f.in`. Symbolic substitution confirms the linear-H teaching solution satisfies q_trial - 3G*Delta p - sigma_y = 0. The local Newton denominator is 3G+H, not 2G+H.
- Recomputed the two study-point Young moduli: 65279.06 MPa for G=24541, and 64606.08 MPa for G=24288, both at nu=0.33. Checked the other worked calculations, 385/1960 parameter counts, case-versus-pooled RMSE distinction, 90-minute exam and 900-second rehearsal totals.
- Compared reported bracket quantities with saved `summary.json` and mesh/porosity studies. Confirmed that different elastic moduli confound the Workbench/USERMAT stiffness comparison and that mesh-dependent reaction peaks are not validated strength.
- Consulted official ANSYS USERMAT documentation and the primary AlSi10Mg microstructure study linked in the source index. These support background teaching, not experimental claims about this bracket.
- Reran the independent model verifier: all checks passed. Regenerated the test report: mean curve RMSE 0.4386287734712186 MPa. Recursive comparison with committed JSON found differences no larger than 1.4210854715202004e-14. Restored only these generated check outputs, preserving saved evidence byte for byte; `git diff --stat reports/` is empty.
- Full pytest rerun: 28 passed, 1 skipped, 8 failures in compiled Fortran-driver execution; 30 subtests passed. Windows Application Control still blocks the native drivers (including WinError 4551). No security policy was bypassed and no new Fortran numerical-pass claim is made.
- Rebuilt corrected short guides, PDFs and all 42 offline cards. Function-level quiz checks cover navigation, answer reveal, rating, filtering, shuffle and reset.

## Textbook edition

`output/pdf/project-textbook.pdf` is published from the same corrected lesson sources by `scripts/build_study_textbook.py`. It has a cover, reading guide, notation table, linked contents, numbered chapters, 16 typeset display equations, saved project figures, page furniture and PDF outline bookmarks. The contents are built in multiple passes so page references resolve. Theory, viva and practical preparation are separate parts. Source lessons and the publication script remain editable and committed.

Visual QA renders the complete final book and checks the page montage and selected full-size pages; PDF extraction checks text stays inside page bounds, navigation exists and the text contains no literal HTML layout tags. Original shorter PDFs are also rebuilt and checked. This is a project-based study edition, not an independently peer-reviewed textbook or a certification of the underlying physical model.
