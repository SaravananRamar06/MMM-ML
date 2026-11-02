# Decisions and requirement record

Date of initial record: **2026-10-24**. "Confirmed" refers to the user's account, not inspection of a written assignment.

| ID | Status | Decision or constraint | Basis / consequence |
| --- | --- | --- | --- |
| D01 | Confirmed | Use professor-supplied AlSi10Mg data for the material ML work. | Dataset is independent of the bracket geometry. |
| D02 | Corrected 2026-10-27 | Intended scope includes material stress–strain prediction and porosity-to-CL functionality; CL means **critical flaw length** (D19). | The porosity-to-CL connection remains unresolved. |
| D03 | Confirmed | Random 50/50 train/test split by simulation case. | Professor's instruction as clarified by user. No row-level split. |
| D04 | Tentative requirement | Choose a neural network; at most two models. | User is unsure of the exact maximum. Do not inherit five old regression comparisons as requirements. |
| D05 | Confirmed | Physics-informed or first-principles methods are optional. | Phrase introduced by user, not professor. Use physics only with justified definitions. |
| D06 | Confirmed | Treat current data folder as complete as supplied. | Do not block on obtaining all 108 matrix outputs. |
| D07 | Evidence handling | Prior presentation results are historical and unverified here. | Professor data was not supplied to Claude; user did not run prior code. |
| D08 | Observed / evidence handling | Longer handoff contains historical code excerpts that may be reviewed. | Their existence changes recoverability, not validation status. |
| D09 | Superseded 2026-10-27 (D19) | CL was recorded as aerodynamic coefficient of lift. | Reversed by the user; see D19. |
| D10 | Working convention | Preserve raw data, submitted PDF, and historical handoffs unchanged. | New documentation records corrections and uncertainties separately. |
| D11 | Working convention | Use training-only preprocessing/tuning and case-level evaluation. | Prevent information leakage and row-count imbalance. |
| D12 | Superseded 2026-10-27 (D19) | Retire the fracture interpretation as the current project target. | Reversed: critical flaw length is the current target again. Original submission files stay preserved. |
| D13 | Research recommendation, 2026-10-24 | First material model: compact query MLP, `(T, log10(rate), density, G, E11) -> Svm`; candidate `5–16–16–1`. | Literature plus all-file audit; not user approval of exact settings or empirical model selection. See `research.md`. |
| D14 | Conditional research recommendation | Reserve a second model for a PCA-coefficient MLP if training-side reconstruction preserves important curve features. | Full-data exploratory PCA is not a final basis or prediction score. Retain case 60. |
| D15 | Implemented | Random 36-training/37-test split, seed 42, three internal case folds; `data/split.json`. | Training-side selection is saved; earlier all-data exploration must still be disclosed. |
| D16 | Selected after bounded comparison | Deliver the Svm query MLP ensemble: five 5–16–16–1 tanh networks, alpha 0.001. | Saved final artifact in `runs/score/final_Svm/`; PCA-coefficient MLP rejected, GP kept as a reference. |
| D17 | User-authorised publishing | Publish code/current results to private MMM-ML; reusable room to private AI-GroupChat. | Claude is MMM-ML publisher; Codex is chat publisher. Exclude raw data and runtime chat/telemetry from exports. |
| D18 | User-confirmed identity | Display the Antigravity/agy collaborator as Gemini (`gemini`). | No Gemini CLI installation is required to name or join the existing agent session. |
| D19 | User correction, 2026-10-27 | CL means **critical flaw length**: the largest defect the bracket can carry at its design stress before fracture. | Overrides D09 and D12. Do not reintroduce aerodynamic lift. C_L0 (Cockcroft–Latham damage) remains a separate quantity. |

## Decisions not yet made

- Exact stress/strain target definitions and unit conversions.
- Meaning of density and modulus variation; whether a porosity mapping is valid.
- Fracture setup for CL: flaw geometry (surface or embedded), fracture toughness K_IC, the stress at the bracket's critical location, and how porosity feeds that stress.
- Whether the professor's tentative two-model limit includes exploratory references; only one final neural-network family is selected.
- Material constants, build/heat-treatment conditions, and bracket coupling.
- Final deadline and verified ANSYS outputs available for the final report.

## Superseded assumptions

- "CL means coefficient of lift" (recorded 24 October 2026) is incorrect for this project. On 27 October the user confirmed CL = critical flaw length (D19).
- "There is no historical code available" is too strong: the longer handoff contains embedded code. There are no standalone recovered/validated scripts yet.
- "The submitted presentation is an ANSYS results deck" is not established: its own provenance slide says Python. Resolve the user's broader submission description separately.
- Historical five-fold CV is not the current required final evaluation; the user clarified a random 50/50 case holdout.

Append future decisions with date, reason, and affected artifacts. Do not turn a proposal into a confirmed requirement without evidence.


## 25 October 2026 — Documentation and retest

- User requested team-voice README text without contribution credits and a simple first-person explanation. Both README source versions now match; existing detailed guides are preserved alongside the new concise guide.
- Keep the delivered predictor and fixed split unchanged. A retest uses a separate in-memory frozen-settings fit and timestamped evidence, with hashes verifying artifact preservation. Repeating the same holdout does not create independent validation.
- User input questions should be posted in the group chat. No scientific definition was invented to complete the documentation.

## 26 October 2026 — Scope of implemented porosity extension
Keep the final material model intact. A density-derived porosity relation requires explicit source confirmation or an explicitly accepted exploratory assumption; require a separate phi/G relation. Imported solver values are identified as supplied evidence. No structural or aerodynamic labels are fabricated from material stress curves, and no further NN is trained before target data exists. CAD face identities are preparation data, not inferred boundary conditions.

## 31 October 2026 — Colab choices and conditional porosity extension

- User-selected: a fresh library-based Colab notebook, scikit-learn, one neural
  network and Svm against E11. The notebook remains planned, not implemented.
- Proposed future porosity route: establish per-case phi provenance first.
  Replace density if phi is an exact transform of it; add a sixth input only
  when phi supplies distinct information and paired response data exists.
  These are conditional recommendations, not a confirmed physical mapping or
  an instruction to train the extension. Preserve the existing model/version.
- User instruction later in the same discussion: "we will assume porosity is
  4%". Adopt fixed nominal `phi = 0.04` as a study assumption, stored in
  `configs/study_assumptions.json`. This does not confirm source-history
  porosity, a reference density or a G(phi) law. Keep this constant in metadata
  rather than adding it as a learned feature. A porosity-dependent extension
  still needs response data spanning known phi values.

## 31 October 2026 — MLP versus PINN, governing equation first

- User requests a step-by-step Colab comparison of MLP and PINN and explicitly
  requires a governing equation before model creation. This replaces the
  single-model Colab choice; the delivered predictor remains preserved.
- User confirms all files are supplied and no original VPSC inputs/run logs
  are available. Do not require further user files to produce the plan.
- Proposed workflow: qualify a sourced constitutive hypothesis on training
  cases before creating networks, then use a common PyTorch implementation
  for a controlled data-loss versus physics-residual comparison.
- No constitutive law is selected yet. Recovery/saturation is a research
  candidate; VPSC-like names/columns do not confirm the generator or its law.
  Fixed 4% porosity does not establish material mappings or equation constants.


## 31 October 2026 - Effective-equation qualification result

User chose "Effective law (Recommended)" and authorized checking it using the 36 training cases before creating MLP/PINN. Preserve the exact 36/37 split. Tested a simple exponential and Hockett-Sherby-type softening adaptation with fitting-only positive condition-dependent maps. Prospective research screens: mean normalized error <5%, worst <10%, baseline improvement, convergence and numerical correctness. Both candidates fail the error screens. Do not create the planned networks with these equations yet. Rejection applies to the tested families/maps/protocol, not all effective laws. Keep 4% porosity as assumed metadata. See effective-equation-check.md.


## 2 November 2026 - Test the single MLP proposal

User selected "MLP equation (Recommended)" and requested "test this" after asking for the best plan. Execute the specified single 5-16-16-1, seed-42 scikit-learn model with alpha selected only on 36 training cases; compare with the existing curve-copy baseline and diagnose omitted condition groups through nested selection. Export the exact empirical equation. Preserve 37 test cases until the selected fitted weights are saved/locked. This is a fresh experiment, not a universal-best-model claim.


## 2 November - Single MLP test conclusion

The specified single MLP improves mean RMSE over the lookup baseline in training-case CV (2.174491 versus 3.602695) and the 37-case test (0.142667 versus 1.378978). It supports within-design interpolation; nested condition holdouts are much weaker, including 43.236012 at 200/-5, and do not justify a universal-best or new-regime claim. The exported JSON equation exactly reproduces the final network. The recovered fit is weight-for-weight identical to the preserved first fit; the rerun addressed reporting only. Keep the previous ensemble and its results as a separate artifact. Hosted Colab remains unverified following a browser policy stop.
