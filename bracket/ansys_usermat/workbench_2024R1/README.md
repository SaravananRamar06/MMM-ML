# Workbench 2024 R1 project: the bracket with the JC-PINN USERMAT

`Bracket_USERMAT_2024R1.wbpj` is a Static Structural project in Ansys Workbench 2024 R1 (v241). It is the team's wing-rib bracket with the locked JC-PINN as an Ansys user material (USERMAT). It was added on 18 November 2026 so that the USERMAT model can be opened in Workbench, which the MAPDL batch decks do not allow. It is a **post-hoc re-run** of the existing study with the same material, supports and load; nothing in the model was tuned.

## What is in the model

| Item | Setting | Same as |
|---|---|---|
| Geometry | `bracket/cad/Rib Bracket.STEP` | team Workbench model |
| Supports | both mounting faces at x = 210 mm fixed (named selection `Fixed_mounting_faces_x210`) | `_FIXEDSU` in `bracket/ansys/.../SYS-2/MECH/ds.dat` |
| Load | whole bore (r = 5 mm) moved UX = -2 mm, Y and Z free (named selection `Bore_UX_minus2mm`) | `d,all,ux,-2.` on the bore nodes |
| Analysis | static, small deflection, auto time stepping, 20 initial / 10 min / 1000 max substeps | `nsub,20,1000,10` |
| Mesh | quadratic SOLID186, 5 mm, swept: 6696 elements, 32233 nodes | 5 mm SOLID186 (7304 elements in the team mesh) |
| Material | command snippet `JC-PINN USERMAT (TB,USER)` under the body: `TB,USER` with 100 degC, 1e-4 /s, density 2592 kg/m3 (phi = 4 %), G 24541 MPa, nu 0.33 (assumed); `TB,STATE` 4 | `make_decks.py` USERMAT snippet |
| Output | `outres,svar,all` (analysis snippet); results: equivalent stress, total deformation, user result `SVAR1` (EQPS), force reaction at the fixed support | |

Engineering Data holds a material `AlSi10Mg JC-PINN USERMAT` (E 65279 MPa = 2G(1 + nu), nu 0.33, density 2592 kg/m3). It only labels the body: the solver uses `TB,USER`.

## Results (`results_2026-11-18/`)

From `summary.json` and `reaction_history.csv`, against the MAPDL batch run on the team's 5 mm mesh (`report/numbers.json`):

| Quantity | Workbench 2024 R1 (this project) | MAPDL batch deck |
|---|---|---|
| Peak reaction | 190.0 kN at UX = -0.455 mm | 190.4 kN at UX = -0.455 mm |
| Reaction at UX = -2 mm | 134.0 kN | 136.7 kN |

- The peak agrees to 0.2 %. After the peak the material softens, so the force depends on the mesh, and the two meshes differ (6696 swept against 7304 elements): 2.0 % at -2 mm.
- At -2 mm the maximum equivalent stress is 134.9 MPa and the maximum SVAR1 (EQPS) is 0.645, at the bore. That is far above the data's strain range (0.0999), so those elements carry the range flag (SVAR3) and are extrapolation.
- `solve.out` confirms `ANS_USER_PATH` and the TB,USER block; `mech_log.txt` is the build log. Pictures: `equivalent_stress.png`, `eqps_svar1.png`, `total_deformation.png` (at 1 s, UX = -2 mm).

## Open, re-solve or rebuild

- **Open:** `open_project.bat` starts Workbench 2024 R1 on this project with `ANS_USER_PATH` set for that process only. The result file (`file.rst`, 78 MB) is not committed, so Mechanical asks to solve before it shows contours.
- **Re-solve:** needs the USERMAT built for MAPDL 2024 R1 (`umat/README.md`; default folder `%USERPROFILE%\jcpinn_usermat_build`). Solving through `open_project.bat` takes about two minutes.
- **Rebuild from scratch:** `build_project.bat` runs `build_project.wbjn` (Workbench) and `mech_setup.py` (Mechanical) in batch: it creates, meshes, solves and saves the project in `%USERPROFILE%\jcpinn_workbench`, and writes the results and pictures there.
- It does not open in Workbench 2024 R1 if saved by a later version; the team's `bracket/ansys/Elastic.wbpj` is 2026 R1 and cannot be opened here.

## Limits

The same limits as the batch study apply: forces after yield are mesh dependent, nu = 0.33 is assumed, one material condition (the study point), small strain, imposed displacement (no service load), and nothing is experimentally validated.
