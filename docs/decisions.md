# Decisions

This file records the decisions behind the final JC-PINN model and this repository, with the date, who made each one, and its effect. Earlier decisions about superseded models are kept on branch `archive/pre-final-2026-11-07` (`docs/decisions.md`), and are summarised in [history.md](history.md).

## Project scope

| ID | Date | Decision | Made by | Effect |
|---|---|---|---|---|
| S1 | Oct 2026 | Use the instructor's AlSi10Mg simulations (`TEAM_8_extracted_results_set_1`, 73 of 108 planned cases) as complete as supplied. | User | The 35 missing conditions are not requested again. |
| S2 | Oct 2026 | Random 50/50 split by simulation: 36 training and 37 test cases, seed 42 (`data/split.json`). | Instructor, via user | The same split is used for every model, so results are comparable. |
| S3 | 27 Oct 2026 | CL means **critical flaw length**, not coefficient of lift. | User | The bracket workflow has no lift path. The material model does not predict CL (no flaw or toughness data). |
| S4 | Oct 2026 | Target: von Mises stress `Svm` along axial strain `E11`, resampled to 120 strains from 0.0002 to 0.0999. | Agreed | Each curve counts equally. |

## The final model (7 November 2026)

| ID | Decision | Made by | Effect |
|---|---|---|---|
| M1 | Use **Equation 1** of the user's customised Johnson–Cook notes as the governing equation. | User | `σ_JC = [A − Bεⁿ][1 + C ln ε̇*][1 − T*ᵐ][G/G₀]^q[1 − φ]^r` |
| M2 | Constants: ε̇₀ = 1e-5 s⁻¹, T_r = 30 °C, T_M = 600 °C, G₀ = 25300 MPa, ρ₀ = 2700 kg/m³. | User (notes) | Fixed in `configs/jc_pinn.json`. |
| M3 | Build: Equation 1 backbone **×** a learned correction exp(δ). | User (chosen over residual or penalty-only forms) | The untrained model is exactly Equation 1. |
| M4 | ε_p = `E11`. ε̇* is the strain-rate ratio ε̇/ε̇₀. | User | There is no elastic segment, so the strain is total. |
| M5 | φ = 1 − ρ/2700 per case (0, 3, 7.85 %); the study point is φ = 4 %. | User | Whether the generator intended density to stand for porosity is still unconfirmed (see open questions). |
| M6 | Selection by a **balanced score**: ½ (case CV + mean of nine temperature/rate group holdouts), on training cases only. | User | The setting has to interpolate and also predict unseen conditions. |
| M7 | Test set: **lock first, score once, disclose** that earlier stages explored it. | User | `selection_lock.json` is written before any test file is read. |
| M8 | Weight decay α = 1 and the trend residual form were fixed from training-fold development checks before the formal run. | Claude, recorded in config | α = 0.001 let exp(δ) blow up. |
| M9 | Selected by the score: **no physics loss (λ = 0), constants trained jointly**. | Protocol | Score 4.166; every physics weight scored worse. |

## After the lock

| ID | Date | Decision | Made by | Evidence |
|---|---|---|---|---|
| A1 | 7 Nov | Run a post-hoc control (same network, Equation 1 off) and report it, even though it scored better. | Claude, accepted | `reports/jc_pinn_20261107/control_no_equation.json` |
| A2 | 7 Nov | Screen for improvements on training cases only: recipe, strain-law floor, correction forms. | Claude | `reports/jc_pinn_20261107/improvement_screen.json`. None beat the locked model. |
| A3 | 7 Nov | **Submit the locked model unchanged.** | User ("the model is fine to submit") | No model changes after the lock. |
| A4 | 7 Nov | Correct the λ = 0 extrapolation note in an errata file rather than editing locked files. | Claude | `reports/jc_pinn_20261107/ERRATA.md`; the lock hash stays valid. |

## Repository (7 November 2026)

| ID | Decision | Made by |
|---|---|---|
| R1 | Rewrite the whole repository, including `main`, around the final model only: code, notebooks, videos, report, paper, slides, README. | User |
| R2 | Archive the earlier state first, on branch `archive/pre-final-2026-11-07` (commit `ee1f001`). A tag was refused by the Git server (403), so the archive is the branch only. | User; tag blocked |
| R3 | Keep the ANSYS project and CAD unchanged, in `bracket/`. Port the porosity workflow and ANSYS bridge to the JC-PINN, and remove the withdrawn lift path. | User |
| R4 | Rewrite both the course report and the IEEE paper for the final model. Generate every number from the saved run. | User |
| R5 | Merge into `main` after all checks. | User |

Append new decisions with the date, who made them, and the evidence.
