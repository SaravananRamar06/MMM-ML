# JC-PINN user material (Abaqus UMAT)

`jc_pinn_umat.f` is an Abaqus/Standard UMAT for the locked JC-PINN. It is generated from the saved weights in `reports/jc_pinn_20261107/equation.json`, so its flow stress is the delivered model, not a refit.

**Status:** verified offline against the Python model with gfortran and a test driver. It has **not yet been run inside Abaqus.** See [verification.json](verification.json).

## What it does

- **Plasticity:** small-strain J2 (von Mises) plasticity with isotropic hardening or softening.
- **Flow stress:** the JC-PINN ensemble, evaluated exactly as in `src/jc_pinn.py`:
  - σ_y = exp(mean_k[ln σ_JC,k + δ_k]) over the five members;
  - inputs are T, log₁₀ ε̇, ρ, G and the strain.
- **Strain mapping:** the model strain is the equivalent plastic strain (decision M4: ε_p = E11).
  - Below 0.0002, σ_y is held at its value there. That value is the initial yield.
  - Above 0.0999, σ_y is held constant and the point is flagged. The model has no data there.
- **Integration:** backward-Euler radial return, with a safeguarded Newton solve.
  - The slope dσ_y/dε̄ₚ is analytic: the chain rule through Equation 1 and both tanh layers.
  - The consistent tangent DDSDDE uses that slope.
  - If Newton fails, the routine sets PNEWDT = 0.25 to ask Abaqus for a smaller increment.
- **Element types:** 3D, plane strain and axisymmetric elements (NDI = 3). Plane stress elements stop with an error message.

Initial yield and flow stress from the model (MPa, inferred units):

| T, ε̇, ρ, G | ε̄ₚ = 0.0002 | 0.05 | 0.0999 |
|---|---:|---:|---:|
| 30 °C, 1e-5 /s, 2700, 25300 | 132.95 | 108.45 | 94.54 |
| 100 °C, 1e-4 /s, 2592 (φ = 4 %), 24541 | 136.06 | 99.39 | 75.41 |
| 200 °C, 1e-3 /s, 2488.05, 23313.95 | 139.75 | 89.51 | 40.86 |

## Material constants

`*USER MATERIAL, CONSTANTS=7` (6 is the minimum), and `*DEPVAR` with at least 4 variables:

| PROPS | Meaning |
|---|---|
| 1 | T, °C. Used when PROPS(6) = 0. |
| 2 | Strain rate, s⁻¹. Fixed, like the case conditions in the data. |
| 3 | Density, kg/m³. Porosity is φ = 1 − ρ/2700. For the 4 % study point, use 2592. |
| 4 | G, MPa. This is the model input and, by default, also the elastic shear modulus. |
| 5 | Poisson's ratio ν. **Assumed**: it is not in the data. About 0.33 is typical for AlSi10Mg. |
| 6 | 0 = take T from PROPS(1); 1 = take T from the temperature field (TEMP + DTEMP). |
| 7 | Optional elastic shear modulus, MPa. 0 = use PROPS(4). |

| STATEV | Meaning |
|---|---|
| 1 | Equivalent plastic strain |
| 2 | Current flow stress, MPa |
| 3 | Range flag, kept for the whole history. It is a sum of: 1 = ε̄ₚ above 0.0999; 2 = T, rate, density or G outside the data range; 4 = 200 < T ≤ 300 °C (no data, unvalidated) |
| 4 | Newton iterations in the last increment |

Example for the 4 % porosity study point at 100 °C:

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

Run with:

```bash
abaqus job=bracket user=umat/jc_pinn_umat.f
```

On Windows, copy the file to `jc_pinn_umat.for`. It is fixed-form Fortran 77 with no modules and no `SAVE` state, so it is safe for threaded runs.

## Limits

- **Softening:** the curves soften. Past the peak, strain localises, so results depend on the mesh. Report the mesh size and check convergence. A regularisation, such as a length scale from CELENT, is not included.
- **Strain is total:** the data's strain is total axial strain E11, which the user's decision reads as plastic strain. The elastic part comes from G and the assumed ν.
- **Range:** the data cover 30–200 °C, 1e-5 to 1e-3 /s, density 2488–2700 and G 23314–25300 MPa. Anything outside is flagged, not clamped. 250 °C drops to about 7 MPa at ε̄ₚ = 0.1, which is unvalidated extrapolation.
- **Fixed strain rate:** the rate is a fixed material constant. The UMAT does not compute the rate from the analysis.
- **Temperature coupling:** DDSDDT and the thermal terms are zero, so the routine is not meant for coupled temperature–displacement steps.
- **Shared project limits:** the units are inferred, the data are simulations, nothing is experimentally validated, and critical flaw length is not predicted.

## Rebuild and check

```bash
python scripts/write_umat.py
```
```bash
python scripts/verify_umat.py
```

`write_umat.py` regenerates the file from `templates/jc_pinn_umat.f.in` and the locked weights. `verify_umat.py` needs gfortran and writes `verification.json`. It checks:

- **Flow stress:** compared with `jc_pinn.equation_predict` at 2000 random points. The largest relative difference was 2×10⁻¹⁵.
- **Slope:** compared with finite differences. The largest relative difference was 3×10⁻⁹.
- **Single-element uniaxial stress:** four conditions, in 3D and 4-component form, with 20 or 1000 increments.
  - The stress stays on the flow curve to about 10⁻¹¹.
  - The results do not depend on increment size, to about 10⁻¹² MPa.
- **Consistent tangent:** compared with finite differences. The largest relative difference was 10⁻¹⁰.
- **Range flags:** each flag is set when it should be.

`tests/test_umat.py` runs the same checks under pytest. It skips the numerical part when gfortran is missing.

**Not covered:** an ANSYS USERMAT wrapper. ANSYS orders the shear components 12, 23, 13 and uses its own interface. The core routines `JCPFLW` and `JCPSIG` can be reused there.
