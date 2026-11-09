# Corrected deck: changes and verification (9 November 2026)

**Input:** `Final Presentation - Porosity in an AM Wing Bracket.pptx` at commit `b56ab26`. The audit (branch `codex/presentation-audit`, commit `118fdf5`) records it as byte-identical to the downloaded copy it reviewed, SHA-256 `7d7165a3…`.

**Output:**
- `Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx`
- the matching PDF

Both are built by `build/build_corrected.js`. The original deck and `build/build_final.js` are unchanged.

**Evidence used:**
- Locked model on `main` (`66b89e0`):
  - `reports/jc_pinn_20261107/results.json`: `selected = {physics: none, lambda_phys: 0.0, theta_mode: joint}`; study point ρ = 2592.
  - `control_no_equation.json`: group mean 5.629 and test 0.3375.
  - Run README, section "Does Equation 1 help?": the selected model's group mean is 6.235.
  - `configs/jc_pinn.json`: variable mapping, T* clipped at 0, φ = 1 − ρ/2700, ε = E11.
  - `bracket/tools/ansys_material_bridge.py`: uses the JC-PINN; describes itself as an "Unvalidated Placeholder".
  - `bracket/workflow/porosity_workflow.py`: uses the JC-PINN.
  - Model Studio: archived, per the main README.
- Presentation sources on this branch:
  - `source/Comparison Study - Final.wbpj`
  - the team's contour screenshots in `source/results/`

No model was retrained, tuned or modified.

## Substantive corrections (audit item → slides)

| Audit item | Correction | Slides |
|---|---|---|
| 1. Physics loss | λ = 0 is shown on the slides. The model is described as a JC-backbone hybrid. A main-body statement says no accuracy benefit from physics is shown: the control is better on groups (5.63 vs 6.23) and test (0.338 vs 0.439). The earlier attribution to "strong weight decay, log-space output" is removed: differences in architecture, output form and regularisation prevent attributing the gap to one ingredient. | 1, 4, 12, 13, 14, 15, 19 + notes |
| 2. Porosity | Porosity is represented through density with the assumed mapping φ = 1 − ρ/2700. The cases are 7.85 / 3 / 0 %; the 4 % study point is ρ = 2592. Removed "porosity fixed at 4 %, not a model input". The r ≈ 0 statement is qualified: the correction network also sees density. | 3, 9, 14, 16, 18 + notes |
| 3/4. Ansys peaks | Peaks are kept as team-screenshot results. The ratio is 1.86× (not 1.85×), about 46 % lower; "halves" and "overpredicts" are removed. The 0.94 % single-peak agreement is stated not to validate the material law, the full response or the coupling. The slide 8 title is replaced. The elastic fixed-corner peak is flagged as a possible singularity. Unarchived set-up (load, mesh, energy balance, supports) is disclosed, and R = F is labelled a static idealisation. | 5, 6, 7, 8, 19 + notes |
| 3 (fracture). CL workflow | The target becomes K_I(a_c) = K_IC for a specified crack geometry and orientation. K_I(a) comes from the crack-opening stress, not peak von Mises. The deck adds an LEFM check (else J) and a pore-to-crack convention. CL is called a static critical crack size, not a fatigue or airworthiness criterion; accept/inspect/reject is labelled a concept. | 3, 4, 8, 17, 18, 19 + notes |
| 6. Material card vs history | E11 (total axial strain) is distinguished from εp. The JC-U card notes that conversion needs a confirmed E and that the table's source is unconfirmed. The rising "our curve" figure is replaced by a schematic of table rows. The softening A − Bεⁿ form is distinguished from standard JC hardening. | 6, 14 + notes |
| 7. Fast-rate claim | The two lowest-error groups are now named: 200 °C · 10⁻³ (0.14) and 30 °C · 10⁻³ (0.18). The slide notes that 100 °C · 10⁻³ is 0.45. | 16 + notes |
| 8. Deployment status | The deck now separates what exists (JC-PINN inference, porosity workflow, material-card writer as an unvalidated template) from what is planned (validated coupling, crack model and K_IC, fatigue, decision tool). Model Studio is described as archived; the incorrect "still serves an MLP" line is removed. | 4, 17 + notes |
| 9. Selection bias, CV wording | Labels now say case cross-validation on the training partition. Group scores are described as used in selection, not independent estimates, with optimism not quantified. | 12, 13, 15, 16 + notes |
| 10. Rounding and equation | The group mean is 6.23 (exact 6.2349). The equation variables are defined (ε̇₀, clipped T*, G₀, φ). The parameter count is 385 network weights and biases + 7 constants = 392 per member, 1,960 in total. Constants are stated not to be separately identifiable. | 12, 13, 14, 16 + notes |
| 11. Ranges and wording | "Any temperature" becomes "within the sampled ranges". "Nothing leaks" becomes "scaler statistics from training cases only". Svm/Evm definitions are refined. "Every curve ends below its start" replaces "stress falls in every curve". | 3, 9, 10, 11, 18 + notes |

**Kept unchanged:** the 20-slide structure, team details, design, both GIF animations, slide 2 and slide 20.

**Verified results kept:**
- mean curve RMSE 0.4386;
- R² 0.9995;
- 94.9 % of points within ±1 source stress unit;
- 37/37 test cases better than the JC equation alone;
- Ansys peaks 595.27 / 320.79 / 323.81 MPa.

**Disclosures kept:**
- units inferred;
- not a blind test;
- selection bias;
- sparse conditions;
- no experimental validation.

## Verification

- `verification.json`: automated checks over all slide text, tables, chart data and speaker notes.
  - They confirm 20 slides with notes on every slide, each required correction, the preserved results, and the absence of stale claims ("never seen", "1.85×", "6.24", "halves", "fixed at 4 %", "still serves an earlier MLP", any ensemble, PCA or Gaussian-process reference).
  - Both GIFs are embedded as `image/gif`: 36 frames / 13.9 s and 37 frames / 27.8 s, looping. **All checks pass.**
- `rendered_slides_*.jpg`: every slide rendered through LibreOffice and inspected. No clipped text was found.
- `slide_text_and_notes.md`: the full extracted text, including speaker notes.
- `validate.py` (OOXML schema, relationship and chart checks) passed.

**Not checked:**
- Playback inside Microsoft PowerPoint Slide Show (no PowerPoint here). GIF frames, timing and the loop flag were checked from the embedded files.
- Native PowerPoint layout. Rendering was checked through LibreOffice with metric-compatible fonts.
- The Windows path `C:\Users\SARAVANAN\Downloads\...` was not accessible from this cloud session. The deck was corrected from its byte-identical source on this branch.
