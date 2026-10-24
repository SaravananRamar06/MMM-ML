# MMM-ML — project handoff

College course: **Multiscale Modelling of Materials using Machine Learning**. Material: **AlSi10Mg**. Current focus: a reproducible ML workflow on professor-supplied material simulations and establishing how porosity relates to the aerodynamic **coefficient of lift, C_L**.

**Critical correction, 2026-10-24:** the user confirmed CL means coefficient of lift. The submitted presentation and historical handoffs incorrectly interpret the project target as critical flaw length. Do not carry that interpretation or its fracture equations into the new model.

## Read in this order

1. [context.md](context.md) — confirmed project scope, people, requirements, and provenance.
2. [tasks.md](tasks.md) — completed work and the next actions.
3. [dataset.md](dataset.md) — observed files, schema, coverage, and interpretation gaps.
4. [methodology.md](methodology.md) — proposed workflow and scientific limits.
5. [open-questions.md](open-questions.md) — information still needed.
6. [decisions.md](decisions.md) — accepted constraints and choices still pending.
7. [logs.md](logs.md) — dated work history.

[AGENTS.md](AGENTS.md) provides project-wide guidance for coding agents.

[research.md](research.md) contains the research conclusion, all-file audit findings, architecture comparison, sources, and proposed model-development workflow.

Later implementation reviews: [saved prediction checks](reports/codex-artifact-check.md) and [selected model reload checks](reports/codex-selected-model-check.md). These verify artifact consistency; they do not replace the research assumptions or resolve the aerodynamic target.

[project-questionnaire.md](project-questionnaire.md) contains all 100 context questions, starting with 12 priorities and prefilling confirmed facts. [COLLABORATION.md](COLLABORATION.md) explains the local browser group chat, Codex usage panel, and invitation for Claude to join and add its own usage provider.

Start the dashboard with `python3 collaboration/group_chat.py serve` from this folder, then open `http://127.0.0.1:8765` on the same computer. Agents use the CLI to post during active turns; the room does not automatically invoke either model.

## Handoff coverage

The current Markdown files capture the project-relevant context from this conversation: the user's clarifications, team responsibilities, submission provenance, CL correction, professor's split instruction, tentative model limit, deadline uncertainty, dataset observations, research conclusion, unresolved questions, and next experiment. This is a structured handoff, not a verbatim chat export. Confirmed facts, historical claims, and recommendations are kept distinct.

The detailed research notes are retained alongside the main report:

- [Constitutive architectures](<research_notes/Neural networks for material curves/constitutive_architectures.md>)
- [Physics and operator alternatives](<research_notes/Neural networks for material curves/physics_and_operators.md>)
- [Dataset-specific evidence](<research_notes/Neural networks for material curves/dataset_fit.md>)
- [Development and validation workflow](<research_notes/Neural networks for material curves/workflow_validation.md>)

For a future session, start with this README, then `AGENTS.md`, `context.md`, `research.md`, and `tasks.md`. The material model and empirical comparison are complete; current implementation details are in the checkpoint at the top of `context.md`.

## Existing source material

| Item | Role |
| --- | --- |
| `TEAM_8_extracted_results_set_1/` | Professor-supplied material data: 108 planned cases, 73 available histories. |
| `AM Porosity in a Wing Rib Bracket.pdf` | Actual submitted presentation, generated using Claude; 16 slides. |
| `AM-porosity-bracket-context.md` | Earlier AI-generated handoff; historical claims require verification. |
| `AM-porosity-bracket-context-more.md` | Longer historical handoff, including embedded solver and fitting code; not executed here. |

## Current status

- Final material predictor: five small query MLPs averaged, each 5–16–16–1, target Svm. Saved in `runs/score/final_Svm/`.
- Fixed seed-42 split: 36 training / 37 test cases; 120 strain points per curve. Saved test mean per-curve RMSE is 0.05908515, worst 0.11330618, in inferred stress units. Codex independently recomputed these saved prediction errors. Earlier full-data exploration means the holdout is not fully blind; condition generalisation is substantially worse.
- Model Studio: **http://127.0.0.1:8766**. Shared room: **http://127.0.0.1:8765**. Both are local services. Agent responses require active sessions.
- Private repositories: [MMM-ML](https://github.com/SaravananRamar06/MMM-ML) and [AI-GroupChat](https://github.com/SaravananRamar06/AI-GroupChat). Claude publishes the model repo; Codex publishes the room repo. Raw data, runtime chat and telemetry are excluded from exports.
- Gemini is the user's Antigravity/agy collaborator, displayed as **Gemini**, and has joined the room. All three usage providers are integrated and available through the live room API. Only Codex has quota snapshots in the currently checked sources; missing quotas remain explicit.
- The corrected presentation is drafted in `reports/presentation/`; numerical/text reviews are saved there. Claude reports the visual corrections applied; Codex verified source text/numbers. Report/viva packaging, confirmed units, ANSYS evidence, and the physical porosity-to-lift connection remain open.

## Resume here

Read the current checkpoint in [context.md](context.md) and [tasks.md](tasks.md), then consume unread room messages before editing shared files. Finish presentation/integration reviews and obtain missing scientific definitions. Do not retrain or resplit merely because older research snapshots say implementation was pending.
