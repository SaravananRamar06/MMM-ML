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

For a future session, start with this README, then `AGENTS.md`, `context.md`, `research.md`, and `tasks.md`. Research is complete for the current recommendation; implementation and empirical model comparison have not started.

## Existing source material

| Item | Role |
| --- | --- |
| `TEAM_8_extracted_results_set_1/` | Professor-supplied material data: 108 planned cases, 73 available histories. |
| `AM Porosity in a Wing Rib Bracket.pdf` | Actual submitted presentation, generated using Claude; 16 slides. |
| `AM-porosity-bracket-context.md` | Earlier AI-generated handoff; historical claims require verification. |
| `AM-porosity-bracket-context-more.md` | Longer historical handoff, including embedded solver and fitting code; not executed here. |

## Current status

- Requirements/provenance discussion, numerical inspection of all 73 histories, and architecture/workflow research are complete.
- Research recommends a compact `E11`-query MLP first and a conditional PCA-coefficient MLP second. This is a recommendation, not a trained-model result or user approval of exact settings.
- Claude has since reported a pipeline and experiments in the shared room. Codex confirmed implementation files and a 36/37 split exist, but has not independently reproduced the modelling results. Review those artifacts before duplicating work.
- The professor's data was **not** given to Claude when it generated the submitted presentation.
- The user did not download or run the prior code. Embedded code in the longer handoff is a recovery source, not evidence of successful execution.
- The professor approved the topic, not the presentation's specific equations, assumptions, or numerical results.
- Final deliverables: working ML model(s), report, presentation, and viva. Deadline is next month relative to 24 October 2026; exact date pending.

## Resume here

Use [research.md](research.md) to settle the material prediction contract and implement the proposed case-level experiment. Physical definitions still need confirmation; no split or model exists yet. In parallel, recover the intended relationship between porosity and lift coefficient and identify aerodynamic labels or a justified calculation. Do not present the old deck's numerical claims as validation of the new workflow.
