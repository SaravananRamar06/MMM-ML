# Critical flaw length of the cracked bracket (20 November 2026)

Post-hoc analysis. The locked JC-PINN is used unchanged as the USERMAT; nothing is retrained or tuned. The load and the toughness were chosen by the user (decisions F1 and F2 in [`docs/decisions.md`](../../../docs/decisions.md)).

## Result

At the bracket's capability-based limit pin load of **35.9 kN**, **no fillet crack up to 30 mm fails, at any porosity**, for K_mat = 36–50 MPa√m. So the critical flaw length (CL) is greater than 30 mm. The crack line leaves the section at about 39 mm (keypoint 31 in each `crack.dat`, 39.2 mm from the crack mouth). The bracket is limited by yield, not by fracture.

- **Weakest case:** a = 30 mm, φ = 7.85 %, K_mat = 36 MPa√m. It carries **44.80 kN** with the first collapse peak and 44.36 kN with the second.
- **Check against the loads:** both values are above the limit load (35.9 kN) and above the limit load times the 1.15 fitting factor (41.3 kN).
- **Reserve factor** P_f / 35.9 kN: the lowest is 1.248 with the first peak and 1.236 with the second.

## How porosity acts (G coupled to φ, decision D5)

1. **Limit load** (first yield at the R10 fillet, from `scripts/check_limit_load.py`): 36.25 / 35.82 / 35.43 kN at φ = 0 / 4 / 7.85 %, a drop of 2.3 %. Chart: `limit_load_phi.png`.
2. **Residual strength P_f against crack length** (K_mat 40 MPa√m, first peak, kN). The table is `residual_strength.csv` and the chart is `residual_strength.png`.

   | a (mm) | 0 | 8 | 16 | 25 | 30 |
   |---|---|---|---|---|---|
   | φ = 0 % | 89.26 | 83.48 | 72.98 | 57.96 | 47.79 |
   | φ = 4 % | 88.01 | 82.64 | 72.49 | 57.44 | 47.29 |
   | φ = 7.85 % | 87.27 | 81.86 | 72.02 | 56.94 | 46.85 |

3. **CL against load, a sensitivity study above the limit load** (K_mat 40, first peak, mm). The table is `cl_vs_load.csv` and the chart is `cl_vs_load.png`.

   | Load (kN) | 50 | 60 | 70 | 80 |
   |---|---|---|---|---|
   | φ = 0 % | 28.91 | 23.93 | 18.17 | 10.66 |
   | φ = 4 % | 28.66 | 23.68 | 17.86 | 10.08 |
   | φ = 7.85 % | 28.44 | 23.45 | 17.55 | 9.52 |

## Method

- **Model** (`crack2d/make_crack_decks.py`):
  - The bracket is a straight 40 mm extrusion, so its x–y section is modelled with PLANE183 in plane strain.
  - The profile comes from `bracket/cad/Rib Bracket.STEP`.
  - A through-thickness edge crack starts at the point of highest tension on the R10 fillet, (31.15, 14.34) mm. It runs radially at −120°, perpendicular to that tension.
  - Crack lengths: a = 1, 2, 4, 6, 8, 12, 16, 20, 25 and 30 mm.
  - The tip has singular quarter-point elements (KSCON), and the mesh elsewhere is 2 mm.
  - Supports and load are as in the 3D runs: the mounting faces are fixed, and UY is imposed on the upper half of the bore.
- **K_I:**
  - Linear elastic run at UY = 0.1 mm, with K_I from the interaction integral (CINT, 6 contours).
  - k(a) = K_I / P is the median of contours 2–6. The contours agree within 0.3 %, except at a = 1 mm, where contour 6 reaches the fillet.
  - k(a) does not depend on E, and so does not depend on porosity.
- **Collapse load P_C(a, φ):**
  - The JC-PINN USERMAT runs at 100 °C and 1e-4 s⁻¹, with ρ and G at φ = 0, 4 and 7.85 % (D5). UY is ramped to 2 mm.
  - P_C is the peak reaction × 40 mm. Two peak definitions are reported, `first` and `second`; see `crack2d/fad_cl.py`.
- **Assessment** (BS 7910 Option 1 FAD):
  - Kr = k(a) P / K_mat and Lr = P / P_C.
  - Failure occurs when Kr reaches f(Lr) = (1 + ½Lr²)^−½ [0.3 + 0.7 exp(−μLr⁶)], with μ = min(0.001 E/σ_y, 0.6).
  - Lr_max = 1, because a softening material carries no load above its peak.
  - σ_y is the first-yield flow stress at each φ: 137.32 / 135.69 / 134.20 MPa, from `scripts/check_limit_load.py`.
- **Worked example** (`fad_cl.json` → `worked_example`): a = 30 mm, φ = 7.85 %, K_mat = 36.
  - Inputs: k = 0.5774 MPa√m/kN, P_C = 49.96 kN and μ = 0.462.
  - At 35.9 kN: K_I = 20.73 MPa√m, Kr = 0.576, Lr = 0.719 and f(Lr) = 0.853. The point lies inside the FAD.
  - At failure, P = 44.80 kN: Kr = f(Lr) = 0.718 and Lr = 0.897.

## Check of the 2D section against the 3D model (`validation_2d_vs_3d.json`)

| Quantity | 2D | 3D | Difference |
|---|---|---|---|
| Elastic stiffness (kN/mm) | 154.3 | 140.8 | +9.6 % |
| USERMAT stiffness, φ 4 % (kN/mm) | 130.1 | 120.0 | +8.4 % |
| USERMAT peak, φ 4 % (kN) | 88.0 | 100.5 | −12.4 % |
| Fillet S1 per kN (MPa/kN) | 3.93 | 4.137 | −5.0 % |

## Caveats

- **The load:** 35.9 kN is a capability bound, not a service load. No aircraft or wing-loads analysis exists.
- **First yield is not mesh converged:** the 2.5 mm mesh gives about 28.5 kN. A lower limit load only lengthens CL, so the conclusion is conservative.
- **The 2D section collapses about 12 % below the 3D model**, which is also conservative. Its fillet tension per kN is 5.0 % below the 3D model's, which is not: scaling every K_I up by 5.2 % (the 3D/2D ratio) still leaves the weakest case at 43.3 kN, above 41.3 kN (computed in `scripts/write_latex_numbers.py`, macro `ClKScaledWeakkN`).
- **The collapse loads scatter by about ±3 %** because the material softens. For example, at a = 1–2 mm P_C is slightly above the uncracked value. At a = 8–20 mm the peak moves from about 0.8 mm to 1.5–1.8 mm of pin displacement.
- **Unconverged runs:**
  - Five runs stopped converging after their peak: a = 30 mm at every φ, and a = 25 mm at φ = 4 and 7.85 %.
  - Their histories were read back from the result files with `crack2d/post_history.mac` (`crack_history_partial.csv`, without the last, unconverged set).
  - In every one, the reaction had already fallen by more than 1 % after the peak.
  - Runs that diverged before their peak were rerun with line search (LNSRCH) and converged.
- **K_mat:** the literature band 36–50 MPa√m. No K_IC(φ) relation is known, so porosity acts only through stiffness and the collapse load. If K_IC were as low as 20 MPa√m, which some studies of LPBF AlSi10Mg report (Paul et al. 2021) but which lies outside the chosen band, CL at 35.9 kN would be about 23.5 mm at every φ (`fad_cl.json` → `low_K_sensitivity`).
- **Not validated:** nothing here is experimentally validated, and the material data are simulations.

## Files

- `runs/<run>/` holds, for each run:
  - `crack.dat`, the MAPDL input;
  - `crack_result.csv`, from the elastic runs;
  - `crack_history.csv` or `crack_history_partial.csv`, from the USERMAT runs.
- Raw solver files (.rst, .db) are not committed.
- `fad_cl.json`, `residual_strength.csv` and `cl_vs_load.csv` are the outputs of `crack2d/fad_cl.py`. The CSV gives the reserve factor for every crack length, φ, K_mat and peak definition.
- The PNG charts are made by `crack2d/plot_cl.py`.

Rebuild:

```bash
python bracket/ansys_usermat/crack2d/make_crack_decks.py RUN_DIR          # then run each crack.dat in MAPDL
python bracket/ansys_usermat/crack2d/fad_cl.py bracket/ansys_usermat/crack2d_2026-11-20/runs bracket/ansys_usermat/crack2d_2026-11-20
python bracket/ansys_usermat/crack2d/plot_cl.py bracket/ansys_usermat/crack2d_2026-11-20
python bracket/ansys_usermat/crack2d/validate_2d.py bracket/ansys_usermat/crack2d_2026-11-20
```
