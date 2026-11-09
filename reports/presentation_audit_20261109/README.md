# Audit of the 20-slide final presentation — 9 November 2026

The principal JC-PINN test results are reproducible. The deck needs scientific and status corrections before submission: disclose the selected zero physics-loss weight, correct the porosity description, qualify the Ansys comparison, and repair the proposed fracture-mechanics connection. No model or presentation was changed during this audit.

## Precisely what was checked

- Input: `Final Presentation - Porosity in an AM Wing Bracket.pptx`, SHA-256 `7d7165a382c0f4f4187c3ac1ec8c5b815f0705a36161b8a522a2751bc0e71f00`.
- The input is byte-for-byte identical to `presentation/Final Presentation - Porosity in an AM Wing Bracket.pptx` at presentation commit **b56ab26b9e033c1effe5eb68d35361fef3c5f0a9**, branch `claude/blissful-knuth-nwvl73`.
- Final-model evidence: **66b89e0beb43ce5e83119f266a56f1d187c329b6**, GitHub `main`; particularly `reports/jc_pinn_20261107/`, `configs/jc_pinn.json`, `data/`, and `bracket/`.
- Read all 20 slides and their speaker notes and inspected embedded figures and GIF frame counts. Visually inspected all 20 pages of the presentation branch's companion PDF. Direct PowerPoint rendering could not open the downloaded file in this automation environment, so this is not a PowerPoint Slide Show/layout verification. GIFs contain 36 training frames and 37 test frames; playback was not tested.
- Independently evaluated the saved equation with NumPy, reconstructed test statistics and selection scores, and rechecked all 73 original raw histories against their manifest hashes and saved interpolated curves. No training, tuning, model selection or new scientific experiment occurred.
- Original source data, the downloaded presentation, and all locked model files were preserved.

## Results that check out

**Slide 15, material prediction:** recomputed from 4,440 saved test queries and independently reproduced from the saved weights:

- 37 test cases, 120 points each.
- Mean per-curve RMSE **0.4386287735**, correctly displayed as **0.44** or **0.439**.
- Pooled point RMSE **0.5035501484**. This differs from the mean of curve RMSEs; keep the deck's explicit metric label.
- R² **0.9995163409**, correctly displayed as **0.9995**.
- **94.9099099%** of points within ±1 source stress unit, correctly displayed as **94.9%**.
- Worst curve RMSE **0.8406385273**, case **10**; maximum point error **2.9003809716**. “Every condition below 1” means condition-average curve RMSE, not every point error.
- JC-only mean test RMSE **7.3656** and all **37/37** JC-PINN curve errors lower than JC-only. The approximately **17-fold** improvement is consistent.
- Saved-weight inference agrees with stored JC-PINN predictions within **2.56 × 10⁻¹³**.
- The 36/37 case split, training-only selection membership, model lock fingerprints and minimum selection score are internally consistent. The lock-before-test ordering is a recorded protocol claim supported by code and saved flags, not an independently witnessed historical event. Prior test exposure remains correctly disclosed.

**Slides 9–11, data:** all **73 raw source hashes match**, with **2,197,000 rows**. Interpolating the raw files onto the saved 120-point grid gives **exactly identical Svm values**. Coverage is 27 cases at 30 °C, 27 at 100 °C, 19 at 200 °C, none at 300 °C. The 200 °C / 10⁻⁵ group contains only case 60. The grid is E11 **0.0002–0.0999** and contributes **4,320 training queries**.

The one-level matched-curve effects reproduce exactly: temperature **22.1146**, rate **17.4514**, G **3.3990**, density **0.18806**, in source stress units. Rounded slide values are appropriate. All curves finish below their starting stress; do not turn this into a claim that every individual step of the irregular case is monotone.

**Slides 12–13, comparisons:** the earlier single-MLP test **0.142667**, single-MLP training CV **2.174491**, and its nine-group mean **11.900010** match project evidence. JC-only case-CV **10.238** and nine-group **13.947** are validation scores, not in-sample training errors. The control's **0.337543** test and **5.629053** group mean match `control_no_equation.json`; its group mean recomputes from the nine saved summaries. Control weights and per-query predictions are not committed, so its inference cannot be independently reconstructed to the same standard as the final model.

**Slide 5, geometry:** the measured report supports envelope **231.5335 × 230 × 40 mm**, volume **778.0446 cm³**, and mass **2.10072 kg** at 2700 kg/m³. A Ø10 mm half-cylinder of thickness 40 mm has area **628.3185 mm²**. The STEP's stored hash differs from the geometry report solely through LF/CRLF line-ending normalization; normalizing to CRLF reproduces the report's original hash. This is not evidence of a geometry change.

**Slides 6–8, Ansys evidence:** the presentation branch's `presentation/source/Comparison Study - Final.wbpj` confirms three AUTODYN Explicit Dynamics systems named **Elastic**, **Built-in JC**, and **User Defined JC**. The source contour screenshots and slide images display **595.27**, **320.79**, **323.81 MPa** at **0.06 s**. Arithmetic checks: elastic/built-in **1.85564**, JC-U versus JC-B difference **0.94143%**, built-in peak reduction versus elastic **46.1102%**. These are screenshot-supported values, not independently reproduced solver results. The required `Comparison Study - Final_files/` folder is not committed.

**Slide 14, training:** architecture 5–16–16–1, five members, geometric averaging, Adam 1,500 steps and L-BFGS maximum 2,500 iterations match the configuration. The saved seed-0 trace loss decreases from **0.1708775** to **0.0027958**, a factor of **61.12**, consistent with “about 60-fold”. The animation is a recorded training trace, not a new training run.

## Corrections, in order of importance

### 1. Slides 12, 14 and 19: disclose the selected physics loss

The locked model selects `physics="none"`, `lambda_phys=0`, `theta_mode="joint"`. The JC backbone is present, but no physics residual penalty is active. Calling it JC-PINN is the established project name; describing the selected result as evidence that a physics penalty improves generalization is unsupported.

Suggested visible sentence: **“Selected JC-backbone hybrid: physics-loss weight λ = 0; seven JC constants and the neural correction are fitted jointly.”**

The final control performs better than the selected model on both reported headline comparisons: **5.629 vs 6.235** on group holdouts and **0.338 vs 0.439** on test. The deck discloses this in small print, but its titles and conclusion still privilege a physics explanation. State prominently: **“These comparisons do not show an accuracy benefit from the JC backbone or physics penalty.”** Differences in architecture/output/regularization/selection recipe prevent a clean causal attribution to any single training ingredient.

Source: `results.json:selected`, `selection_lock.json`, `control_no_equation.json`, run README section “Does Equation 1 help?”. Keep the locked model unchanged, as required by decision A3.

### 2. Slide 18: porosity is not fixed at 4% across the data/model

“Porosity is fixed at 4% as an assumption, not a model input” is incorrect for the final model. There are five inputs including density, and the user's chosen mapping **φ = 1 − ρ/2700** enters the JC backbone. The case values are **0%, 3%, 7.85%**; the **4%** study point corresponds to **ρ = 2592 kg/m³**.

Replace with: **“Porosity is represented through density using the assumed mapping φ = 1 − ρ/2700. We illustrate a 4% study point; the source dataset's physical porosity interpretation remains unconfirmed.”**

Also qualify the statement about r ≈ 0: r belongs to the separable backbone, while the correction network also receives density. A near-zero r does not prove that the entire trained model is independent of density or that real pores have negligible mechanical effects. Source: config variable mapping, study point, decisions M5, and the independently rechecked small density sensitivity.

### 3. Slides 3, 8 and 17: do not insert peak von Mises stress directly into Mode-I CL

The outline `a_c = (1/π)[K_IC/(Yσ)]²` is appropriate only for a specified Mode-I crack model and compatible stress definition. The deck's route identifies σ with the bracket's peak von Mises stress at the bore. Equivalent von Mises stress is not automatically the tensile stress opening a specified crack. Bore stresses are nonuniform, and the geometry factor must be consistent with whether nominal, local or path-based stress is used.

Replace the route with: **“Specify crack geometry/orientation and loading; obtain K_I(a) from an appropriate analytical solution or FE fracture analysis; solve K_I(a_c) = K_IC, after checking LEFM validity.”** Define whether a is a crack depth, radius or half-length; do not compare it directly with a CT pore diameter without a pore-to-crack convention. If local plasticity is significant, assess an elastic-plastic fracture measure such as J instead. This remains planned work.

The claimed service concern is cyclic flight loading (slide 2). A static critical flaw size alone is not a fatigue-life or airworthiness acceptance criterion. The accept/inspect/reject scheme on slide 17 must remain a concept pending fatigue, margins and validation.

Sources: [Ansys fracture-parameter definitions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/ans_frac/frac_parmcalctypes.html), [AFGROW handbook: stress concentrations and nonuniform crack-path stresses](https://www.afgrow.net/applications/dtdhandbook/sections/page11_4_1.aspx).

### 4. Slides 6, 8 and 19: peak agreement does not verify the material law or coupling

The **0.94%** arithmetic is correct. One scalar peak at one instant does not show that the two constitutive models, curves, deformation histories or failure behavior agree. In particular, the JC-U hardening table's source is explicitly unconfirmed; it cannot be called a verified JC-PINN-driven bracket result.

Replace the slide 8 title with **“The supplied JC runs have similar peak stresses at 0.06 s”**. Replace “our curve matches Ansys” with **“JC-U peak differs from built-in JC by 0.94%; the table's provenance and full response remain to be checked.”**

“Elastic overpredicts” assumes one model represents truth. Safer: **“The elastic run gives a 1.856× higher peak than the built-in JC run.”** “Halves” is approximate; **“reduces the peak by about 46%”** is precise. A large fixed-corner peak may depend on constraint singularity and mesh resolution; the missing companion folder prevents a convergence check.

At two decimal places the direct elastic/built-in ratio rounds to **1.86**, not 1.85. A comparison with the average of both plastic peaks is about 1.85; identify that denominator if retaining it.

### 5. Slides 5–8: the explicit loading/solve is not reproducible from the committed evidence

The `.wbpj` confirms project structure and material property names, not the load value or complete setup. The companion folder with material numbers, mesh, setup, solver outputs and results is absent. The deck's **F has no numerical magnitude**, waveform/ramp, or service-load source. Identical mesh, load and supports across systems are therefore not independently verified.

Add a concise limitation: **“Ansys contours supplied by the team. Load history, mesh convergence, energy balance and material-card provenance are not verified from the archived setup.”** For an explicit simulation intended to approximate a service/static state, check kinetic versus internal energy, reactions including inertia, and sensitivity to mass scaling/loading rate before using its stress as a static design input. `R = F` is a static equilibrium assumption, not a general identity during a transient.

The earlier `bracket/ansys/Elastic.wbpj` on main is a separate static project; its solver input contains `antype,0` and imposed displacement `d,all,ux,-2.`. It must not be used as proof of the explicit bore-load setup. Source: presentation README, source `.wbpj`, main bracket README and solver inputs. [Ansys guidance on mass scaling and quasi-static explicit energy](https://lsdyna.ansys.com/mass-scaling/).

### 6. Slides 6 and 17: distinguish a material history from an Ansys plasticity card

The material predictor learns **Svm versus total axial E11**, with no supplied elastic origin. Standard JC plasticity instead uses equivalent plastic strain and plastic strain rate. The project's custom softening Equation 1 deliberately uses E11 and **A − Bεⁿ**; this is different from standard hardening JC **A + Bε_pⁿ**. Do not silently equate them.

The rising “our curve, point by point” illustration on slide 6 is especially misleading: the supplied histories and learned target generally decrease with E11. Label the figure **“schematic tabular material, not the supplied ML curve”** or replace it with the actual confirmed receiving material table. A bridge script's ability to write CSV/APDL/XML does not validate the receiving model, stress/strain conversion, softening treatment or solver import.

Slide 6's speaker notes state the customised-law table provenance as a fact despite the visible caveat saying it is unconfirmed. Apply the source uncertainty to the notes as well. The other corrections in this report likewise apply to the matching speaker notes.

The minimal conversion ε_p ≈ ε_total − σ/E itself requires compatible uniaxial stress/strain definitions and confirmed E; the current multicomponent Svm/E11 history cannot be assumed compatible. Source: `bracket/tools/ansys_material_bridge.py`, config mapping and [Sandia standard JC definitions](https://www.sandia.gov/files/sierra/SM_LAME_5_20/main/models/johnson_cook.html).

### 7. Slide 16: the “fast rates” statement is false as written

“The best groups are the fast rates (0.14–0.18)” omits **100 °C / 10⁻³**, whose group RMSE is **0.4537**. The best two groups happen to be **200 °C / 10⁻³: 0.1431** and **30 °C / 10⁻³: 0.1816**.

Replace with **“The two lowest-error test groups are 200 °C / 10⁻³ and 30 °C / 10⁻³.”** The weakest group's **0.8031**, with one training and eight test cases at 30 °C / 10⁻⁴, is correct.

### 8. Slides 4 and 17: reconcile completed work with planned deployment

Slide 4 presents “Deploy: a bracket-check tool for aerospace companies” as part of the life cycle already followed. Slide 17 correctly says it is not yet built. Mark slide 4 deployment **“planned”**, and mark material-to-bracket-to-CL coupling **“proposed”**.

The slide 17 footnote says updating the app to JC-PINN is planned. On current main, the maintained **material bridge and porosity workflow already use the locked JC-PINN**; the older Model Studio is archived. The integrated aerospace acceptance/CL tool is still absent. Replace with **“JC-PINN inference and a material-card writer exist; validated Ansys coupling and CL decision support remain planned.”** No claim about a currently running app session is established by this audit.

### 9. Slides 12–13: distinguish validation, training fit and selection bias

The **10.24**, **2.17**, and **2.10** scores in the model-choice plot are **case cross-validation errors on the training partition**, not in-sample training-fit errors. Replace “even on training cases” / “fits familiar conditions (2.17)” with explicit **“training-side case-CV mean curve RMSE”**.

The JC-PINN group mean was used to select among 14 settings, while the earlier single MLP's group diagnostics nested alpha selection. The group comparison is useful but not an unbiased independent model-superiority test. Replace “mildly optimistic” with **“used in selection; optimism is not quantified”**. Keep the existing non-blind test disclosure.

### 10. Slides 12–14, 16 and 19: fix rounding and complete the equation definition

- The exact JC-PINN group mean is **6.234866068**. Correct two-decimal rounding is **6.23**, not **6.24**; **6.235** at three decimals is also appropriate.
- Slide 14 should define **T* = max[(T−30)/(600−30), 0]**, **φ = 1−ρ/2700**, **G₀ = 25300**, and **ε̇₀ = 10⁻⁵** with units. State that ε is E11, an operational total-strain coordinate, rather than asserting that it is equivalent plastic strain.
- “385 weights” should read **“385 network weights and biases per member, plus seven jointly fitted JC constants”**: **392** trainable values per member, **1,960** across five members.
- Readable parameter names do not make the jointly trained constants independently identified material properties. Backbone/correction contributions are not uniquely identifiable; interpret them together. The project's own run report explicitly acknowledges this.

### 11. Slides 3, 9, 11 and 18: tighten remaining range/definition wording

Replace “for any temperature…” with **“within the sampled temperature/rate/density/G and strain ranges; sparse conditions need separate caution”**. A good random split does not validate arbitrary conditions, cyclic histories or plastic constitutive integration.

Slide 11's “nothing about the test set leaks in” is too broad given acknowledged historical exposure. Say **“scaler statistics are fitted only on the training cases.”**

Slide 18 groups the “meaning of Svm” among entirely unknown definitions. Numerical checks already establish consistency with the von Mises invariant of the supplied Cauchy components. More precise: **“Svm's physical units, spatial averaging and generating solver remain unconfirmed; Evm is not established as accumulated plastic strain.”**

## Presentation legibility

The companion PDF shows no obvious clipped major text at the inspected scale. Slides **5, 6, 12 and 14** are dense; equations and limitations are small. Put λ = 0 and the control outcome into the main body rather than the small footer. Keep essential mathematical definitions and uncertainty visible to the audience. PDF inspection cannot establish native PPTX rendering or animated playback.

## Verification record and limits

Run from the audit worktree:

```powershell
& 'C:/Users/SARAVANAN/OneDrive/Documents/ChatGPT/MMM-ML/.venv/Scripts/python.exe' -B scripts/audit_final_presentation.py --pptx 'C:/Users/SARAVANAN/Downloads/Final Presentation - Porosity in an AM Wing Bracket.pptx' --raw 'C:/Users/SARAVANAN/OneDrive/Documents/ChatGPT/MMM-ML/TEAM_8_extracted_results_set_1'
```

`verification.json` records the full numerical checks and slide text. The existing `scripts/verify_jc_pinn.py` computes the checks successfully but its final JSON serialization fails on a NumPy boolean in this Windows environment. The audit evaluates the same independent NumPy calculations without changing that script or the locked run, explicitly includes NumPy booleans in its pass/fail aggregation, and writes only its own evidence folder. This is a verifier portability issue, not a changed prediction or metric.

The required full test report was also regenerated in an excluded scratch copy, preserving `reports/jc_pinn_20261107/`. Every field in its rebuilt `test_summary.json` agrees with the committed report within relative/absolute tolerance 1e-9. The full pytest attempt gives **19 passed, 1 skipped, 26 subtests passed; 7 PyTorch-dependent failures**: PyTorch was initially missing; after installing CPU-only PyTorch into excluded scratch, Windows Application Control blocks `torch/lib/shm.dll` (WinError 4551). The full suite is therefore **not certified as passing here**. No OS policy was changed. NumPy inference, raw-data checks and the test-report reconstruction complete independently of PyTorch.

This audit confirms numerical reproduction, source-curve identity, source-document agreement and screenshot transcription. It does not establish experimental material validity, solver convergence, fatigue life, aircraft certification or a finished CL predictor. No raw data, downloaded PPTX, model coefficients or protected run files are added/modified by this audit.
