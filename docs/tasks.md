# Task tracker

Last updated: **2026-10-24**. Checkboxes denote completed work, not anticipated results.

## Completed in this session

- [x] Create a 100-question context questionnaire, local chat/document dashboard, Codex usage provider, and Claude extension interface.
- [x] Verify six persistence/API/provider tests and live HTTP endpoints; read and acknowledge Claude's first room message.
- [x] Review Claude's implementation, split, saved selection history, predictions, and model reloads. Earlier full-data exploration is disclosed.
- [x] Locate project folder and inventory source files.
- [x] Read the original handoff and extract the submitted PDF text.
- [x] Inspect matrix values, output coverage, row counts, and selected histories.
- [x] Clarify material, team roles, intended outputs, professor's split instruction, and submission provenance with user.
- [x] Identify embedded code and relevant method/results sections in the longer handoff; do not execute it.
- [x] Create persistent project instructions, context, data notes, methodology, decision log, questions, and activity log.
- [x] Numerically inspect all 73 histories and save a reproducible read-only audit with per-case results.
- [x] Research architecture alternatives and the full development/validation workflow; save findings in `research.md` with primary sources.

## Next: establish the data and target definitions

- [x] Build a reproducible case inventory and numerical-quality audit; retain unconfirmed units as provisional. Raw-file hashes remain part of implementation preparation.
- [x] Plot representative curves and identify initial nonzero stress, general decline, and case-60 irregularity. Their physical explanation remains unconfirmed.
- [ ] Establish the generating solver/material law, loading protocol, output averaging, and strain/stress definitions where possible.
- [ ] Recover or justify the density/modulus-to-porosity interpretation; do not assign labels by assumption.
- [ ] Recover the professor's intended connection between porosity/material response and coefficient of lift, plus the aerodynamic setup and label source.
- [ ] Review any useful historical code selectively; the old fracture workflow is not the current CL target. Assess completeness and correctness before recovery/run.
- [ ] Record the final prediction contract: inputs, outputs, units, and valid range for each capability.

## Then: implement and evaluate

- [x] Fix 36/37 allocation and seed 42; save `data/split.json` by available simulation ID.
- [x] Use 120 strain queries per case and training-fitted preprocessing.
- [x] Select compact query MLP, five-member 5–16–16–1 tanh ensemble, alpha 0.001, target Svm.
- [x] Complete bounded PCA-coefficient MLP comparison; reject it on training-side scores. GP is an interpolation reference.
- [x] Save training-side case-CV and condition-holdout scores/configuration, with earlier full-data exploration disclosed.
- [x] Save final 37-case scoring for the fixed model, per-case errors, and supplemental condition diagnostics. Do not call the test set fully blind.
- [x] Save inference artifacts; independently reload selected models and reproduce saved predictions/metrics.
- [x] Run focused PCA-MLP isolation/reload tests and Model Studio live parsing/inference checks. Unit definitions remain unconfirmed.

The research experiment has now been executed. See `reports/codex-selected-model-check.md`, `reports/presentation/codex-fact-check.md`, and `runs/score/`. Physical definitions remain necessary before constitutive or aerodynamic claims.

## Current collaboration work

- [x] Publish private MMM-ML and AI-GroupChat repositories with reproducible code/results and scope documentation.
- [x] Register and receive posts from Gemini, the user's Antigravity/agy session; preserve its requested display name.
- [x] Implement Codex and Claude usage providers, participant registry, and safe Markdown rendering.
- [ ] Review/integrate Gemini's actual available telemetry; do not manufacture counters if unavailable.
- [ ] Review and publish Claude's latest visual/output improvements and colour changes in AI-GroupChat.
- [ ] Confirm desktop launcher behaviour on the user's desktop; code review/dry-run does not establish successful real agent launch.
- [ ] Incorporate Codex/Gemini fact-checks into the final visual presentation. Draft/source files exist.
- [ ] Pool and prioritise shared-state/task-card and token-efficiency improvements after current integration is stable.

## Final deliverables

- [ ] Inspect teammate's actual ANSYS project/results and reconcile material constants, boundary conditions, and solved status.
- [ ] Establish any material-to-bracket coupling before claiming multiscale validation.
- [ ] Write a report with reproducible methods, evidence-backed results, assumptions, and limitations.
- [ ] Correct the submitted presentation's wrong critical-flaw-length interpretation of CL, then rebuild relevant figures and numerical claims from saved, verified outputs.
- [ ] Prepare viva explanations of neural networks, splitting/leakage, losses, generalisation, physical assumptions, and multiscale transfer.
- [ ] Confirm exact deadline and deliverable format before packaging submission.

## Awaiting user or teammate information

- Exact final date; described as next month on 24 October 2026.
- Any professor wording/notebook note on coefficient of lift versus porosity, neural-network/model-count expectations, or data definitions.
- Aerodynamic dataset, coefficient definition/reference quantities, geometry, and operating conditions, if provided separately.
- Any original dataset message, companion files, or generating-code documentation that can be recovered.
- Teammate's actual ANSYS files and exported results; user said further material would come later.
- Clarification of the earlier "only ANSYS results" description versus the submitted Python-provenance PDF.

These pending items do not prevent independent material-data auditing. Missing aerodynamic labels and an unresolved material-to-lift connection prevent an evidence-backed lift-prediction claim.
