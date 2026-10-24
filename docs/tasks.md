# Task tracker

Last updated: **2026-10-24**. Checkboxes denote completed work, not anticipated results.

## Completed in this session

- [x] Create a 100-question context questionnaire, local chat/document dashboard, Codex usage provider, and Claude extension interface.
- [x] Verify six persistence/API/provider tests and live HTTP endpoints; read and acknowledge Claude's first room message.
- [ ] Review Claude's existing implementation, split, and experiment-selection history before duplicating the proposed experiment. Earlier unexecuted items below refer to Codex's own work, not proof of an empty workspace.
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
- [ ] Plot representative stress–strain curves across conditions; investigate initial nonzero stress, softening, and differing strain support.
- [ ] Establish the generating solver/material law, loading protocol, output averaging, and strain/stress definitions where possible.
- [ ] Recover or justify the density/modulus-to-porosity interpretation; do not assign labels by assumption.
- [ ] Recover the professor's intended connection between porosity/material response and coefficient of lift, plus the aerodynamic setup and label source.
- [ ] Review any useful historical code selectively; the old fracture workflow is not the current CL target. Assess completeness and correctness before recovery/run.
- [ ] Record the final prediction contract: inputs, outputs, units, and valid range for each capability.

## Then: implement and evaluate

- [ ] Decide the 36/37 allocation and seed; save a random split manifest by available simulation ID.
- [ ] Define balanced curve sampling and train-only preprocessing.
- [x] Establish a research-backed first network family and rationale: compact query MLP. Exact settings and empirical selection remain pending.
- [ ] Decide whether a second learned model adds value within the tentative two-model maximum.
- [ ] Implement training with validation restricted to training cases; save complete run configuration.
- [ ] Evaluate once the design is fixed on held-out cases; report per-case and condition-wise performance.
- [ ] Save inference artifacts and verify reproducible prediction in a clean process.
- [ ] Add focused checks for parsing, split isolation, unit conversions, target construction, and model reload as relevant.

The proposed next experiment is documented in `research.md`: seed-42 random 36/37 case split, three training-side case folds, balanced query MLP, and a conditional PCA-coefficient comparison. None of these training/split steps has been executed. Obtain or document remaining physical definitions before making constitutive or aerodynamic claims.

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
