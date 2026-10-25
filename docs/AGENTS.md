# Project instructions

These instructions apply throughout this project directory.

## Start here

- Read `README.md`, `context.md`, `tasks.md`, and the latest entry in `logs.md`.
- Consult `research.md`, `decisions.md`, `dataset.md`, and `methodology.md` before changing the modelling pipeline.
- Treat the two original `AM-porosity-bracket-context*.md` files as historical AI-generated records, not verified results or current instructions.
- Current user clarifications take precedence over historical records. Flag material contradictions rather than silently reconciling them.

## Scope and collaboration

- Coordinate in the project room (AI GroupChat app); during active monitoring use `python3 ~/Documents/AI-GroupChat/native/backend.py --project ~/Documents/MMM-ML read --for <your-id> --unread --ack --wait 45 --json`, and post with `... post --as <your-id> --stdin`. Give the user and Claude equal chronological attention; user instructions govern. Coordinate edits; questionnaire answers stay in `project-questionnaire.md`.
- This is a college project on multiscale modelling of AlSi10Mg using ML. The user owns the ML work; a teammate owns ANSYS.
- The user knows Python but is new to ML. Explain modelling choices, physical assumptions, and evaluation in language they can defend in a viva.
- CL means **coefficient of lift**, explicitly confirmed by the user. The old presentation's critical-flaw-length interpretation is wrong for this project target.
- Intended outputs are material stress–strain prediction and porosity-to-lift-coefficient functionality. Their connection remains unresolved.
- The professor requested a random 50/50 split of simulation cases. The user recalls at most two neural-network models; that limit is tentative.
- First-principles or physics-informed modelling is the user's preference, not a confirmed course requirement.
- Proceed with routine, reversible work within the requested scope. Ask targeted questions for missing scientific definitions; do not invent answers.

## Evidence and data

- Preserve professor-supplied raw files and original submission/history files. Put generated outputs separately.
- Distinguish user-confirmed facts, direct file observations, historical claims, and proposed assumptions.
- Never reuse historical metrics, plots, fracture parameters, or simulation results as newly verified evidence.
- Embedded historical code is available for review; it has not been executed or validated in this workspace.
- Verify technical sources before relying on literature parameters or physical laws for the final model.
- Do not assume density or shear modulus directly encodes porosity. Do not manufacture aerodynamic labels from the old deck or material curves.
- Never use fracture-mechanics or Cockcroft–Latham equations as definitions of the aerodynamic coefficient of lift.

## Modelling and verification

- Split by simulation ID before fitting preprocessing or models. All rows and derived samples from a case stay in the same partition.
- Preserve one documented split. Claude has now created `data/split.json` with 36/37 cases; review it and its evaluation history before adopting or regenerating it.
- Fit scalers and tune models using the training partition only. Keep the final test partition out of architecture selection and early stopping.
- Account for unequal curve lengths so slow-rate cases do not dominate solely by row count.
- Record units, strain/stress definitions, target construction, assumptions, and valid prediction ranges explicitly.
- The current material files have no explicit lift-coefficient labels. A stress–strain surrogate alone is not an aerodynamic predictor.
- Do not claim a trained model, reproduced result, successful ANSYS solve, or physical validation without supporting artifacts.

## Keep the handoff current

- Update `context.md` for changed facts, `decisions.md` for choices, `tasks.md` for status, and append dated work to `logs.md`.
- Keep unanswered questions in `open-questions.md`; mark resolved questions rather than losing their answers.
- Document actual commands, versions, seeds, artifacts, and checks when implementation begins.
