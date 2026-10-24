# Decisions and requirement record

Date of initial record: **2026-10-24**. "Confirmed" refers to the user's account, not inspection of a written assignment.

| ID | Status | Decision or constraint | Basis / consequence |
| --- | --- | --- | --- |
| D01 | Confirmed | Use professor-supplied AlSi10Mg data for the material ML work. | Dataset is independent of the bracket geometry. |
| D02 | Corrected by user | Intended scope includes material stress–strain prediction and porosity-to-C_L functionality; C_L means **coefficient of lift**. | Earlier "both" answer was followed by explicit clarification. The aerodynamic connection remains unresolved. |
| D03 | Confirmed | Random 50/50 train/test split by simulation case. | Professor's instruction as clarified by user. No row-level split. |
| D04 | Tentative requirement | Choose a neural network; at most two models. | User is unsure of the exact maximum. Do not inherit five old regression comparisons as requirements. |
| D05 | Confirmed | Physics-informed or first-principles methods are optional. | Phrase introduced by user, not professor. Use physics only with justified definitions. |
| D06 | Confirmed | Treat current data folder as complete as supplied. | Do not block on obtaining all 108 matrix outputs. |
| D07 | Evidence handling | Prior presentation results are historical and unverified here. | Professor data was not supplied to Claude; user did not run prior code. |
| D08 | Observed / evidence handling | Longer handoff contains historical code excerpts that may be reviewed. | Their existence changes recoverability, not validation status. |
| D09 | Confirmed definition | CL means aerodynamic **coefficient of lift**. | Do not substitute critical flaw length or Cockcroft–Latham damage from the old deck. |
| D10 | Working convention | Preserve raw data, submitted PDF, and historical handoffs unchanged. | New documentation records corrections and uncertainties separately. |
| D11 | Working convention | Use training-only preprocessing/tuning and case-level evaluation. | Prevent information leakage and row-count imbalance. |
| D12 | User correction, 2026-10-24 | Retire the fracture interpretation as the current project target. | Coefficient of lift was explicitly confirmed. Preserve original submission files, but correct the new handoff. |
| D13 | Research recommendation, 2026-10-24 | First material model: compact query MLP, `(T, log10(rate), density, G, E11) -> Svm`; candidate `5–16–16–1`. | Literature plus all-file audit; not user approval of exact settings or empirical model selection. See `research.md`. |
| D14 | Conditional research recommendation | Reserve a second model for a PCA-coefficient MLP if training-side reconstruction preserves important curve features. | Full-data exploratory PCA is not a final basis or prediction score. Retain case 60. |
| D15 | Proposed experiment, not executed | Random 36-training/37-test split, proposed seed 42, three internal case folds. | Respect professor's half-case split; keep tuning/transforms inside training. Disclose existing full-data EDA. |

## Decisions not yet made

- Exact stress/strain target definitions and unit conversions.
- Meaning of density and modulus variation; whether a porosity mapping is valid.
- Aerodynamic setup, material/porosity-to-lift connection, and source of lift-coefficient labels.
- Exact architecture/activation, framework, loss, preprocessing, and curve sampling; recommended network family is now documented in `research.md`.
- Whether one or two learned models are needed and how they connect.
- Locking/executing the proposed split seed and allocation; no manifest exists yet.
- Material constants, build/heat-treatment conditions, and bracket coupling.
- Final deadline and verified ANSYS outputs available for the final report.

## Superseded assumptions

- "CL means critical flaw length" is incorrect for this project. The user confirmed coefficient of lift. Earlier tentative acceptance of the PPT interpretation does not override this correction.
- "There is no historical code available" is too strong: the longer handoff contains embedded code. There are no standalone recovered/validated scripts yet.
- "The submitted presentation is an ANSYS results deck" is not established: its own provenance slide says Python. Resolve the user's broader submission description separately.
- Historical five-fold CV is not the current required final evaluation; the user clarified a random 50/50 case holdout.

Append future decisions with date, reason, and affected artifacts. Do not turn a proposal into a confirmed requirement without evidence.
