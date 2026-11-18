# Workbench 2024 R1 project: the bracket with the JC-PINN USERMAT

`Bracket_USERMAT_2024R1.wbpj` is a Static Structural project in Ansys Workbench 2024 R1 (v241). It holds the team's wing-rib bracket, with the locked JC-PINN as an Ansys user material (USERMAT). It was added on 18 November 2026 so that the USERMAT model can be opened in Workbench, which the MAPDL batch decks do not allow. It is a **post-hoc re-run** of the batch study with the same material, supports and load. Nothing in the model was tuned.

**Load (corrected on 18 Nov 2026).** The pin load is +P_y, the wing-normal upload, and it bears only on the half of the bore that faces it. The model therefore imposes UY = +2 mm on the upper half-face of the bore. The STEP splits the bore at y = 0, so that is face 86, with its centroid at y > 0. UX and UZ are free. The team's Workbench file had UX = -2 mm on the whole bore. The first version of this project used that load. Its results are kept in `results_2026-11-18/` as evidence only.

## What is in the model

| Item | Setting | Same as |
|---|---|---|
| Geometry | `bracket/cad/Rib Bracket.STEP` | team Workbench model |
| Supports | both mounting faces at x = 210 mm fixed (named selection `Fixed_mounting_faces_x210`) | `_FIXEDSU` in `bracket/ansys/.../SYS-2/MECH/ds.dat` |
| Load | upper half of the bore moved UY = +2 mm, X and Z free (named selection `Bore_upper_half_UY_plus2mm`) | `make_decks.py --load plus_y` (bore nodes with y >= 0) |
| Analysis | static, small deflection, auto time stepping, 20 initial / 10 min / 1000 max substeps | `nsub,20,1000,10` |
| Mesh | quadratic SOLID186, 5 mm, swept: 6696 elements, 32233 nodes | 5 mm SOLID186 (7304 elements in the team mesh) |
| Material | command snippet `JC-PINN USERMAT (TB,USER)` under the body: `TB,USER` with 100 degC, 1e-4 /s, density 2592 kg/m3 (phi = 4 %), G 24541 MPa, nu 0.33 (assumed); `TB,STATE` 4 | `make_decks.py` USERMAT snippet |
| Output | `outres,svar,all` (analysis snippet). Results: equivalent stress, total deformation, the user result `SVAR1` (EQPS), and the force reaction at the fixed support | |

Engineering Data holds a material `AlSi10Mg JC-PINN USERMAT` (E 65279 MPa = 2G(1 + nu), nu 0.33, density 2592 kg/m3). It only labels the body; the solver uses `TB,USER`.

## Results (`results_uy_2026-11-18/`)

These come from `summary.json` and `reaction_history.csv`. They are compared with the MAPDL batch run on the team's 5 mm mesh, with the same load (`../results_uy_2026-11-18/`, `report/numbers.json`).

| Quantity | Workbench 2024 R1 (this project) | MAPDL batch deck |
|---|---|---|
| Initial stiffness | 120.0 kN/mm | 120.0 kN/mm |
| Peak reaction | 102.9 kN at UY = 1.22 mm | 100.5 kN at UY = 1.150 mm |
| Reaction at UY = 2 mm | 93.0 kN | 86.3 kN |

- **Stiffness.** The elastic stiffness agrees, so the supports, load and USERMAT stiffness are the same in both models.
- **Peak.** The peak agrees to 2.3 %. Each peak is resolved only to the substep spacing.
- **After the peak.** The material softens, so the force depends on the mesh. The two meshes differ (6696 swept against 7304 elements), and at 2 mm they are 7.8 % apart. The batch mesh study shows the same sensitivity.
- **Stress and plastic strain.** At 2 mm the maximum equivalent stress is 136.1 MPa. The maximum SVAR1 (EQPS) is 0.148, at the loaded half of the bore. That is above the data's strain range (0.0999), so those elements carry the range flag (SVAR3) and are extrapolation.
- **Logs and pictures.** `solve.out` confirms `ANS_USER_PATH` and the TB,USER block, with 0 errors; `mech_log.txt` is the build log. The pictures (`equivalent_stress.png`, `eqps_svar1.png`, `total_deformation.png`) are at 1 s, UY = 2 mm.

## Open, re-solve or rebuild

- **Open:** `open_project.bat` starts Workbench 2024 R1 on this project with `ANS_USER_PATH` set for that process only. The result file (`file.rst`) is not committed, so Mechanical asks to solve before it shows contours.
- **Re-solve:** this needs the USERMAT built for MAPDL 2024 R1 (`umat/README.md`; default folder `%USERPROFILE%\jcpinn_usermat_build`). Solving through `open_project.bat` takes about two minutes.
- **Rebuild from scratch:** `build_project.bat` runs `build_project.wbjn` (Workbench) and `mech_setup.py` (Mechanical) in batch. It creates, meshes, solves and saves the project in `%JCPINN_WB_DIR%` (default `%USERPROFILE%\jcpinn_workbench`), and writes the results and pictures there.
- **Versions:** the project does not open in Workbench 2024 R1 if a later version saved it. The team's `bracket/ansys/Elastic.wbpj` is 2026 R1 and cannot be opened here.

## Limits

The same limits as the batch study apply:
- forces after yield are mesh dependent;
- nu = 0.33 is assumed;
- one material condition only (the study point), with small strain;
- an imposed displacement, not a service load;
- nothing is experimentally validated.
