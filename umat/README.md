# JC-PINN user material (Abaqus UMAT and ANSYS USERMAT)

Two user materials for the locked JC-PINN, generated from the saved weights in `reports/jc_pinn_20261107/equation.json`. Their flow stress is the delivered model, not a refit.

| File | Solver | Entry point |
|---|---|---|
| `jc_pinn_umat.f` | Abaqus/Standard | `UMAT` |
| `jc_pinn_usermat3d.F` | ANSYS Mechanical APDL / Workbench | `usermat3d` |

Both files contain the same core: `JCPRM` (the return mapping), `JCPFLW` (flow stress with range handling) and `JCPSIG` (the five-member network and Equation 1). Only the thin solver wrapper differs.

**Status:** both are verified offline against the Python model, using gfortran and a test driver (see [verification.json](verification.json)). **Neither has been run inside Abaqus or ANSYS yet.**

## What the material does

- **Plasticity:** small-strain J2 (von Mises) plasticity with isotropic hardening or softening.
- **Flow stress:** the JC-PINN ensemble, evaluated exactly as in `src/jc_pinn.py`:
  - σ_y = exp(mean_k[ln σ_JC,k + δ_k]) over the five members;
  - inputs are T, log₁₀ ε̇, ρ, G and the strain.
- **Strain mapping:** the model strain is the equivalent plastic strain (decision M4: ε_p = E11).
  - Below 0.0002, σ_y is held at its value there. That value is the initial yield.
  - Above 0.0999, σ_y is held constant and the point is flagged. The model has no data there.
- **Integration:** backward-Euler radial return, with a safeguarded Newton solve.
  - The slope dσ_y/dε̄ₚ is analytic: the chain rule through Equation 1 and both tanh layers.
  - The consistent tangent uses that slope.
  - If Newton fails, the routine asks for a smaller increment: PNEWDT = 0.25 in Abaqus, `keycut = 1` (bisection) in ANSYS.
- **Elements:** 3D, plane strain and axisymmetric (three direct components).
  - Abaqus stops with an error message for plane stress.
  - ANSYS only calls `usermat3d` for these element types anyway.
- **Shear order:** Abaqus orders the shear components 12, 13, 23 and ANSYS 12, 23, 13. Isotropic J2 treats all shear components the same way, so one core serves both.

Initial yield and flow stress from the model (MPa, inferred units):

| T, ε̇, ρ, G | ε̄ₚ = 0.0002 | 0.05 | 0.0999 |
|---|---:|---:|---:|
| 30 °C, 1e-5 /s, 2700, 25300 | 132.95 | 108.45 | 94.54 |
| 100 °C, 1e-4 /s, 2592 (φ = 4 %), 24541 | 136.06 | 99.39 | 75.41 |
| 200 °C, 1e-3 /s, 2488.05, 23313.95 | 139.75 | 89.51 | 40.86 |

## Material constants and state variables (both solvers)

| Constant | Meaning |
|---|---|
| 1 | T, °C. Used when constant 6 = 0. |
| 2 | Strain rate, s⁻¹. Fixed, like the case conditions in the data. |
| 3 | Density, kg/m³. Porosity is φ = 1 − ρ/2700. For the 4 % study point, use 2592. |
| 4 | G, MPa. This is the model input and, by default, also the elastic shear modulus. |
| 5 | Poisson's ratio ν. **Assumed**: it is not in the data. About 0.33 is typical for AlSi10Mg. |
| 6 | 0 = take T from constant 1; 1 = take T from the analysis temperature (end of increment). |
| 7 | Optional elastic shear modulus, MPa. 0 = use constant 4. |

| State variable | Meaning |
|---|---|
| 1 | Equivalent plastic strain |
| 2 | Current flow stress, MPa |
| 3 | Range flag, kept for the whole history. It is a sum of: 1 = ε̄ₚ above 0.0999; 2 = T, rate, density or G outside the data range; 4 = 200 < T ≤ 300 °C (no data, unvalidated) |
| 4 | Newton iterations in the last increment |

## Abaqus

```
*MATERIAL, NAME=ALSI10MG_JCPINN
*DEPVAR
 4,
 1, EQPS, "Equivalent plastic strain"
 2, SIGY, "Flow stress"
 3, FLAG, "Range flag"
 4, NITER, "Newton iterations"
*USER MATERIAL, CONSTANTS=7
 100., 1.E-4, 2592., 24541., 0.33, 0., 0.
```

```bash
abaqus job=bracket user=umat/jc_pinn_umat.f
```

On Windows, copy the file to `jc_pinn_umat.for`. It is fixed-form Fortran with no modules and no saved state, so it is safe for threaded runs.

## ANSYS (Mechanical APDL and Workbench)

`jc_pinn_usermat3d.F` replaces the example `usermat3d.F` that ships with ANSYS's User Programmable Features (UPF). The build uses ANSYS's own scripts and the Intel Fortran compiler version that your ANSYS release requires. The exact steps depend on the release, so check them against the *Guide to User-Programmable Features* for your version.

1. **Copy the example files.** Make a build folder. Copy into it ANSYS's `usermat.F` and the other `usermat*.F` examples. In 2024 R1 (v241) they are in `<ANSYS install>\ansys\customize\user\` on Windows. Older releases and Linux may use a `winx64` or `linx64` subfolder.
2. **Swap in our routine.** Add `jc_pinn_usermat3d.F`, renamed to `usermat3d.F`, and make sure the stock `usermat3d` is gone.
   - In some releases the stock routine is a separate `usermat3d.F`. Replace that file.
   - In v241 it sits inside `usermat.F`, together with `usermat1d`, `usermatbm`, `usermatps` and `usermat_harm`. Delete the block from `*deck,usermat3d` to its matching `end` in your copy of `usermat.F` (lines 535–934 in v241). Otherwise the link sees `usermat3d` twice.
3. **Build the library.** In that folder, run `ANSUSERSHARED.bat` (Windows; in v241 it is in `ansys\custom\user\winx64\`) or `ANSUSERSHARED` (Linux). This builds `usermatLib.dll` or `libusermatLib.so`.
   - The v241 script expects ifort from oneAPI 2023 (`IFORT_COMPILER23`) and Visual Studio 2019.
   - If only `ifx` is available, `ansys_test/results_2026-11-17/build_ifx.bat` runs the same compile and link steps with `ifx`. That is how the tested library was built.
4. **Point ANSYS at it.** Set the environment variable `ANS_USER_PATH` to the build folder before starting ANSYS or Workbench.

**Tested:** MAPDL 2024 R1 with ifx 2026.2 and VS 2019 Build Tools, on 17 November 2026. The single-element test below passes, with S11 within 1.2×10⁻⁵ MPa of the offline result at all 240 substeps. See `ansys_test/results_2026-11-17/README.md`.

**Mechanical APDL input:**

```
TB,USER,1,1,7              ! material 1, 1 temperature, 7 constants
TBTEMP,0
TBDATA,1,100,1.0E-4,2592,24541,0.33,0
TBDATA,7,0
TB,STATE,1,,4              ! 4 state variables
```

**Workbench (Mechanical):** add a Command Snippet under the bracket body. It overrides the material the solver uses for that body:

```
TB,USER,matid,1,7
TBTEMP,0
TBDATA,1,100,1.0E-4,2592,24541,0.33,0
TBDATA,7,0
TB,STATE,matid,,4
```

- **Engineering Data:** keep an isotropic elasticity entry there that is consistent with the constants, E = 2G(1 + ν). For the example above that is about 65,279 MPa. Workbench expects one, but the solver uses the stiffness returned by the USERMAT.
- **Results:** state variables appear as SVAR1 to SVAR4 in user-defined results. Equivalent plastic strain also appears as the usual plastic strain results, because the routine returns `epsPl` and `epseq`.
- **Elements:** the Workbench default SOLID187 or SOLID186 elements are supported.

**First test in ANSYS:** `ansys_test/single_element.mac` pulls one SOLID185 cube to ε₁₁ = 0.12 at the 4 % study point and writes `jcpinn_single_element.csv`. Then run `python ansys_test/compare.py jcpinn_single_element.csv`. It checks the result against `expected_single_element.csv`, which comes from the offline driver, to within 0.1 MPa. The expected final value is S11 = 75.41 MPa at EQPS = 0.1188, with flag 1 because the strain passes 0.0999. Start MAPDL from inside the run folder, because `-o` is relative to the current folder, not to `-dir`. To read state variables in your own decks, add `OUTRES,SVAR,ALL`, because `OUTRES,ALL` does not write them.

## Limits

- **Softening:** the curves soften. Past the peak, strain localises, so results depend on the mesh. Report the mesh size and check convergence. No regularisation is included.
- **Strain is total:** the data's strain is total axial strain E11, which decision M4 reads as plastic strain. The elastic part comes from G and the assumed ν.
- **Range:** the data cover 30–200 °C, 1e-5 to 1e-3 /s, density 2488–2700 and G 23314–25300 MPa. Anything outside is flagged, not clamped. 250 °C drops to about 7 MPa at ε̄ₚ = 0.1, which is unvalidated extrapolation.
- **Fixed strain rate:** the rate is a fixed constant, not computed from the analysis.
- **Thermal coupling:** the thermal tangent terms are zero, so the routine is not meant for coupled thermal–structural steps.
- **ANSYS coverage:** only `usermat3d` is provided. Plane stress, beams and shells are not.
- **Shared project limits:** the units are inferred, the data are simulations, nothing is experimentally validated, and critical flaw length is not predicted.

## Rebuild and check

```bash
python scripts/write_umat.py
```
```bash
python scripts/verify_umat.py
```

`write_umat.py` regenerates both files from `templates/` (`jc_pinn_core.f.in` plus one wrapper per solver) and the locked weights. `verify_umat.py` needs gfortran. It compiles each file with `test/umat_driver.F` (`-DANSYS` selects `usermat3d`) and writes `verification.json`. The results were the same for both solvers:

- **Flow stress:** compared with `jc_pinn.equation_predict` at 2000 points. The largest relative difference was 2×10⁻¹⁵.
- **Slope:** compared with finite differences. The largest relative difference was 3×10⁻⁹.
- **Single-element uniaxial stress:** four conditions, in 3D and 4-component form, with 20 or 1000 increments.
  - The stress stays on the flow curve to about 10⁻¹¹.
  - The results do not depend on increment size, to about 10⁻¹² MPa.
- **Consistent tangent:** compared with finite differences. The largest relative difference was 10⁻¹⁰.
- **Range flags:** each flag is set when it should be.
- **ANSYS plastic strain:** the returned tensor matches the uniaxial values (p, −p/2) to 10⁻¹⁷.

`tests/test_umat.py` runs the same checks for both solvers under pytest. It skips the numerical part when gfortran is missing.
