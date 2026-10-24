# Professor-supplied dataset

Inspection date: **2026-10-24**. Raw data location: `TEAM_8_extracted_results_set_1/`.

## Provenance and status

- User confirms professor-supplied AlSi10Mg material data, independent of bracket geometry.
- User confirms the supplied folder is complete as received. Missing matrix cases are therefore a property of the available dataset, not a confirmed download fault.
- Generating solver, constitutive model, loading setup, microstructure, units documentation, and any additional accompanying material are currently unknown.
- This initial inspection read the matrix, output headers, row counts, and selected start/end values. It was not a full numerical-quality audit of every field.
- **User-confirmed target correction:** CL means aerodynamic coefficient of lift. No explicit lift-coefficient labels, aerodynamic forces, or flow-condition columns are present in the listed schema. How these material histories support that target remains unresolved.

## Subsequent all-file research audit — 2026-10-24

The initial inspection above was followed by a reproducible numerical inspection of all 73 histories. All entries are finite; all `E11` sequences strictly increase and match prescribed rate times time within `4e-8`. Exact common measured `E11` support is `[0.0001, 0.09999996]`. Every case ends below its initial `Svm`; case 60 has 237 negative `Evm` increments despite increasing `E11`. `Svm` matches the recorded Cauchy components' von-Mises combination within about `9.85e-7` relative error. Physical units and the generating model remain unconfirmed.

See [research.md](research.md), the [read-only script](<research_notes/Neural networks for material curves/inspect_curves.py>), and [numerical output](<research_notes/Neural networks for material curves/curve_inspection.json>). Exploratory all-data PCA describes low-rank shape structure; it is not a final preprocessing basis or prediction result. No split or model was created.

## Matrix schema

File: `simulation_matrix.csv`. One row per planned simulation.

| Column | Observed values | Interpretation status |
| --- | --- | --- |
| `Simulation_ID` | 1–108 | Joins to `simulation_XXXX/STR_STR.OUT`. |
| `temperature` | 30, 100, 200, 300 | Appears to be Celsius from comparison with sampled `TEMP`; verify. |
| `strain_rate` | 0.00001, 0.0001, 0.001 | Appears consistent with axial strain/time in sampled rows; units and precise rate definition need confirmation. |
| `density` | 2700, 2619, 2488.05 | Presumed density; units and physical meaning unconfirmed. |
| `shear_modulus` | 25300, 24541, 23313.95 | Presumed shear modulus; units and role unconfirmed. |

Full matrix size: `4 × 3 × 3 × 3 = 108` cases. Density and shear modulus vary independently in the design.

The lower density values are 0.97 and 0.9215 times 2700; the modulus values use the same ratios. These are numerical observations only. They do not prove that either parameter is a porosity proxy.

If density were bulk density and 2700 were an appropriate fully dense reference, `phi = 1 - rho/rho_solid` would give 0, 0.03, and 0.0785. This is a **conditional candidate mapping**, not an established label definition.

## Coverage

| Matrix temperature | Planned | Output files present |
| --- | ---: | ---: |
| 30 | 27 | 27 |
| 100 | 27 | 27 |
| 200 | 27 | 19 |
| 300 | 27 | 0 |
| Total | 108 | 73 |

Missing IDs: **55–59, 61–63, 82–108** (35 cases). No extra output IDs were observed.

| Rows per output, excluding header | Number of files |
| --- | ---: |
| 100,000 | 19 |
| 10,000 | 27 |
| 1,000 | 27 |

Total observed data rows: **2,197,000**. Longer histories correspond to lower prescribed rates in inspected examples; count alone must not determine their training weight.

## Output schema

Each `STR_STR.OUT` is a whitespace-separated table using scientific notation, with 16 columns:

| Columns | Provisional meaning |
| --- | --- |
| `TIME` | Simulation time; unit unconfirmed. |
| `Evm` | Equivalent strain measure; formula and whether total/plastic unconfirmed. |
| `Svm` | Equivalent stress measure; presumed von Mises, unit unconfirmed. |
| `E11 E22 E33 E23 E13 E12` | Strain components; measure and shear convention unconfirmed. |
| `SCAU11 SCAU22 SCAU33 SCAU23 SCAU13 SCAU12` | Cauchy stress components suggested by header; units and averaging unconfirmed. |
| `TEMP` | Temperature; sampled values 303.15, 373.15, 473.15 suggest Kelvin. |

## Quality questions already visible

- Simulation 1 starts near `Evm = 9.95e-7` with `Svm ≈ 133.3` in unknown stress units. Do not assume the curves include an initially unstressed elastic segment.
- Simulation 1 ends near `Evm = 0.099606`; simulation 60 ends near `Evm = 0.086140` despite both having 100,000 rows. Check what the strain measures mean before resampling or defining common support.
- Final stress can be lower than initial stress in sampled curves. Do not impose monotonic hardening merely because historical notes used Johnson–Cook hardening.
- Establish numerical validity, strain support, curve shape, and tensor/equivalent consistency with documented conventions before choosing targets.

## Evaluation constraint

Professor-requested protocol: **random 50/50 split of simulation cases**. With 73 histories this means 36/37, with the allocation and seed explicitly recorded. No split manifest exists yet.

Rows, resampled points, augmented samples, and derived labels from one case must stay together. Fit transforms on training cases only. Report case-level curve errors as well as any pointwise metrics. A model trained on the available files has no directly tested support at 300°C.
