# Activity log

Append dated entries with actions, evidence, outcomes, and unresolved issues. Avoid credentials or private account details.

## Latest entry — 2026-10-24 — Independent inference/artifact review during chat monitoring

- Confirmed both earlier prediction archives reproduce all saved random-split summary error metrics, with disjoint 36/37 IDs and three training-side selection folds. Saved `reports/codex-artifact-check.md`.
- Created and ran `.venv/bin/python reports/check_selected_artifacts.py`: all four selected joblib models reproduce their saved 37-case predictions and mean/median/worst RMSE values. Results saved in `reports/codex-selected-model-check.md`.
- No models were fitted or modified by these checks. Units, original-data interpretation, selection-history disclosure, final target/model decision, and aerodynamic-label requirements remain unresolved.
- Answered the user's training-progress and both-agents-status questions in the shared room; continued chronological active waits with equal attention to user and Claude.

## Latest entry — 2026-10-24 — Dark mode and equal-attention monitoring

- Added dark/light theme toggle, system-default theme, localStorage persistence, dark surfaces/controls, and explicit read acknowledgements.
- User first requested user-priority reading, then changed to equal attention for themselves and Claude. Replaced the user-first queue/highlighting with chronological incoming-message reading for either participant and a neutral latest-message banner.
- Added `read --for AGENT --unread --ack --wait 45 --json`, with waits capped at 55 seconds and receipts written only by the acknowledging agent. No external model calls or automatic idle-session wake mechanism added.
- Restarted local dashboard in retained session 27022. All 12 tests, JavaScript syntax, and live HTTP checks pass; no visual browser verification was available.
- Read Claude's report and saved metrics JSONs, confirmed fitted model/prediction files exist for both targets, and replied to the user's training-progress message in the room. No fits were independently rerun. Flagged that earlier all-data exploration cannot be erased by subsequent training-only CV.
- Notified Claude that equal attention supersedes earlier user-first instructions and supplied the bounded-wait command. Codex is keeping the current turn active to receive room input.

## Latest entry — 2026-10-24 — Questionnaire and live shared dashboard

- Created `project-questionnaire.md` with 100 ordered questions/answer fields, 12 priorities, known facts, and unknown/decide-for-me options.
- Built `collaboration/group_chat.py`, `index.html`, and `COLLABORATION.md`: atomic Markdown messages, CLI posting/reading, browser conversation, replies/search, allowlisted document viewing, and Markdown export.
- Built only Codex's usage provider after the user assigned Claude its own panel. Usage reads selected-session token-count/limit metadata, not credentials or transcript contents; it does not estimate costs. Documented a hot-discovered optional Claude provider interface.
- Started localhost dashboard in retained server session 3362 at `http://127.0.0.1:8765`. Kept it running for user access. Native escalation was required because the sandbox blocked local sockets.
- Six focused tests pass, plus JavaScript syntax and live HTML/messages/documents/usage/export checks. CUA had no browsers; opening IAB returned `Browser is not available: iab`, so visual rendering was not claimed.
- Claude posted modelling findings and ownership of src/data/runs/figures/.venv. Codex confirmed those directories and a 36/37 split exist, replied with coordination and evidence/target-alignment concerns, and requested a separate findings report before shared-doc merges.
- Claude's model results are reported, not independently reproduced. Updated startup guidance/current-state notes to avoid treating research-completion no-implementation statements as current facts. No additional material models were trained by Codex during dashboard work.
- User asked to open the dashboard soon and discuss there; server is live, direct browser opening is unavailable in this tool session. Invitation and usage extension instructions are ready for Claude.

## 2026-10-24 — Initial study and context gathering

### Request

User asked to study `mmm-ml` and ask detailed questions to recover the full project context. After several rounds, user requested persistent Markdown files such as agent instructions, context, logs, and tasks.

### File inspection

- Located project at `/home/sarvn/Documents/MMM-ML`.
- Read `AM-porosity-bracket-context.md`.
- Extracted all 16 slides of `AM Porosity in a Wing Rib Bracket.pdf` with `pdftotext -layout`.
- Inspected `simulation_matrix.csv`, all output-file row counts, and selected initial/final output values with Python 3 standard-library code.
- Found 108 matrix rows, 73 output histories, 35 missing IDs, and 2,197,000 data rows.
- Found and inspected relevant sections of `AM-porosity-bracket-context-more.md`, including historical solver and model-fitting code. Did not execute embedded code or validate historical results.
- Checked Git status: project directory was not a Git repository.

### User clarifications

- AlSi10Mg data is professor-supplied material data, unrelated to the specific part geometry.
- User initially accepted both stress–strain prediction and the proposed CL functionality. A later same-day correction explicitly identified CL as coefficient of lift; the initial critical-length interpretation was superseded (see correction entry below).
- Professor requested random 50/50 selection of cases for train/test and a suitable neural network; maximum of two models is the user's tentative recollection.
- Data folder is complete as supplied.
- Professor approved the topic only. First-principles wording came from the user.
- Submitted PDF was generated using Claude without the supplied dataset. User did not download/run prior code.
- User handles ML, teammate handles ANSYS. User is comfortable with Python and new to ML.
- Deadline described as next month; exact date pending. Additional teammate material will be provided later.

### Findings and corrections

- PDF explicitly attributes the reported computations to Python rather than ANSYS; how it relates to the user's earlier ANSYS-only submission description is unresolved.
- Old 28% versus later 36% capacity-loss claims are historical versions; neither has been reproduced here.
- Initially no standalone historical code was found. The longer handoff does contain code text, so recovery may be possible; availability does not prove execution.
- Initial planning focused on fracture because of the old deck; that target interpretation was subsequently corrected by the user. Professor data has no explicit aerodynamic CL labels.
- Historical five-fold evaluation and multiple regression candidates do not override current user-confirmed split instructions.

### Documentation created

`AGENTS.md`, `README.md`, `context.md`, `dataset.md`, `methodology.md`, `decisions.md`, `tasks.md`, `open-questions.md`, and `logs.md`.

Original source data, PDF, and historical handoffs were preserved. No neural networks trained, cases split, ANSYS files modified, dependencies installed, or historical numerical results validated.

### Documentation checks

Verified all nine new files exist, local Markdown links resolve, fenced code blocks are balanced, and `AGENTS.md` remains under 50 lines. These are documentation checks, not scientific/model validation.

### Suggested next action

Perform a reproducible curve-quality/definition audit and define the material prediction contract. In parallel, resolve porosity interpretation and the intended aerodynamic CL workflow. See `tasks.md` for the ordered backlog.

## 2026-10-24 — User correction: CL means coefficient of lift

- User corrected CL twice as an aerodynamic quantity, then explicitly confirmed **coefficient of lift**.
- This overrides the submitted PDF, legacy handoffs, and earlier assistant planning that interpreted CL as critical flaw length.
- Updated all new planning documents and agent instructions to use aerodynamic C_L. Retained original submission/history files unchanged as provenance records.
- Removed fracture-label generation from the active methodology. Kept the old equation only as an explicitly superseded interpretation that must not be used for lift labels.
- Preserved material stress–strain prediction, random 50/50 case splitting, and the tentative maximum of two networks.
- Remaining question: how the professor intended porosity/material data to connect to lift coefficient, and where aerodynamic targets/conditions come from. No connection or labels have been invented.

## 2026-10-24 — Architecture discussion before implementation

- User proposed applying ML fundamentals to create a model, then explicitly steered the work to deciding which neural network suits the task first.
- Reviewed existing project instructions and checked installed libraries. Python 3.10.12, NumPy 1.21.5, SciPy 1.8.0, Matplotlib 3.5.1, and pytest 6.2.5 are available; scikit-learn, PyTorch, and pandas are not installed in the checked interpreter.
- No training scripts, processed datasets, saved split, or model were created. No dependencies were installed.
- Discussed a small MLP as the provisional material-surrogate recommendation, with sequence models conditional on demonstrated loading-history dependence and physics-informed training conditional on established equations.
- Architecture is under discussion, not experimentally selected. The user has not approved an exact architecture or a second model.
- Consulted primary sources: scikit-learn's supervised neural-network guide, PyTorch's LSTM documentation, and the original PINN authors' project page. These inform architecture distinctions, not verification of material physics.
- Next action: settle the prediction formulation and architecture rationale before implementation; preserve the unresolved aerodynamic-data requirement.

## 2026-10-24 — Research-backed model development recommendation

- User asked for deeper research on how to create a model for this specific project and requested findings in root `research.md`.
- Synthesised primary literature on feed-forward/recurrent constitutive surrogates, physics-based structure, operator networks, and curve compression, plus official validation/preprocessing/persistence guidance.
- Reproducible read-only inspection covered all 73 output files and 2,197,000 rows. All entries are finite, `E11` increases throughout, all cases finish below initial `Svm`, and case 60 has reversing `Evm`. Exact common measured `E11` support is `[0.0001, 0.09999996]`.
- Research recommends a compact query MLP first, candidate `5–16–16–1` (385 parameters), and a conditional training-only PCA-coefficient MLP second. This is not empirical proof of a winner or approval of exact settings.
- Proposed evaluation is random 36 training/37 test cases, seed 42, three internal case folds, equal case weighting, and original-unit curve metrics. No split or model has been created; seed/allocation remain proposals.
- Full-dataset exploratory PCA is explicitly labelled descriptive. It is not reusable operational preprocessing, held-out accuracy, or a final rank selection. Future reporting must disclose that full-data EDA occurred.
- Saved `research.md` and updated README, methodology, decisions, tasks, context, and dataset notes. Preserved raw data, submitted PDF, and historical handoffs.
- Documentation checks passed: local links resolve across all eight updated files, fenced blocks are balanced, report has 1,713 words and 10 distinct external sources, key counts match the saved audit JSON, and the candidate parameter count is 385. No training claims were checked because no model exists yet.
- Next work is the controlled experiment described in `research.md`, with remaining physical definitions tracked and no invented aerodynamic labels. CL remains coefficient of lift.

## 2026-10-24 — Full-context handoff check

- User asked whether all context had been saved as Markdown.
- Checked the handoff against the conversation: course/material, responsibilities, Python/ML familiarity, professor instructions, tentative model limit, data completeness, submission provenance, explicit coefficient-of-lift correction, research findings, unresolved scientific definitions, and implementation status are documented.
- Added a coverage statement and links to all four detailed research notes in README; added the research report to agent startup guidance.
- Recorded the user's research-before-implementation preference and clarified the now-established all-file stress observation in open questions.
- The files are a structured project handoff, not a verbatim transcript. No training, split creation, or source-data changes occurred during this check.

## 2026-10-24 — Final model checks, publishing, Gemini and presentation review

- Final Svm model selected: five 5–16–16–1 query MLPs averaged, alpha 0.001, fixed 36/37 seed-42 case split and 120 strain queries. Bounded PCA-MLP experiments did not improve selection scores. Earlier all-data exploration remains disclosed.
- Codex independently reloaded four earlier selected artifacts, reproduced saved predictions/metrics, and then recomputed final test RMSEs from `runs/score/final_Svm/test_predictions.npz`: mean 0.0590851517, worst 0.1133061791 (case 45). Recomputed six candidates' saved CV and condition aggregates. No fitting repeated during these checks.
- Model Studio live HTTP/inference checks passed (three tests). Material-to-lift capability, scientific units, physical validation and ANSYS evidence remain unresolved.
- User authorised private GitHub publishing: Claude owns MMM-ML export/push; Codex owns AI-GroupChat export/push. AI-GroupChat commits fbcdcd0 and a1498e1 were pushed; runtime messages, personal telemetry/configuration and raw data were excluded.
- Added dynamic participants and registered Gemini. User clarified this is Antigravity/agy, displayed as Gemini. Gemini actually posted and saved an independent presentation review.
- Codex saved `reports/presentation/codex-fact-check.md`, identified rounding/metric/physical-claim corrections, and requested the same fixes in the visual deck. This was numerical/text review, not visual PowerPoint QA.
- Claude owns current UI CSS/HTML, improved output formatting, colour revisions and desktop launcher. Codex added `/assets/room-ui.js` to both server source allowlists, and guided Gemini/Claude on usage-provider scope and unavailable telemetry. Existing live backend requires deliberate restart before the new external asset route can be used.
- Standalone chat Python suite: `python3 -m unittest discover -s collaboration -p 'test_*.py' -v`, 19 passed. Current late UI changes require separate review before publishing; browser/desktop behaviour is not established by the Python suite.
- Updated README/context/decisions/tasks to prevent stale “no model exists” snapshots from misleading future sessions.

## 2026-10-24 — Three-agent dashboard integration published

- Added receipt-safe `read --brief` and `read --id` plus ROOM_STATE checkpoints; pushed AI-GroupChat commit `4fc2639`. Previews and out-of-order exact-ID reads refuse --ack to avoid advancing the unread watermark.
- Reviewed Gemini's Antigravity adapter; requested/remediated explicit selection, no heuristic transcript search, no fabricated zero telemetry, and cached parsing. Registered it in both participant registries; real session selector remains only in ignored live configuration. Verified actual live HTTP /api/usage returns available Codex/Claude/Gemini.
- Researched Slack/Linear layouts and primary Fluent/W3C motion guidance; saved generic `docs/UI_DESIGN.md` in AI-GroupChat. Claude implemented space/density/panel controls and reduced-motion guards. Codex inspected after.png; no claim of independent full interactive-browser QA.
- Fixed safe Markdown emphasis and ordered-list start numbers visible in the screenshot. Added per-quota snapshot timestamp, derived remaining percentage, and reset-passed warning that current quota is unknown. Claude/Gemini quotas remain unavailable from checked local sources, not unlimited or zero.
- Final check: 25 Python tests, 6 Markdown tests, 3 quota-state JS tests, six inline scripts and both external scripts pass syntax checks. AI-GroupChat commit `6665365` pushed successfully; working tree clean.
- Direct final model reload reproduced all 37 archived predictions exactly (max difference 0.0). Corrected presentation source now incorporates remaining wording/rounding fixes; Claude reports visual deck republished.
- User confirmed the desktop launcher opens all three sessions successfully. Claude reports MMM-ML push `5df212a`; the new handoff checkpoint/log update is ready for its next coordinated export.

## 2026-10-24 — Demo and end-of-day handoff

- Independently checked final-model case 42 and generated `figures/demo_case42.png` plus reproducible `reports/check_demo_case.py`. Corrected demo.py's nearest-grid-versus-0.05 point display; no training or metrics changed. Full details in `reports/demo-verification.md`.
- Added local PNG artifact rendering to AI-GroupChat, with name/path/symlink/size/type boundaries and tests. Restarted only the identified room server and verified the actual PNG HTTP response. Messages/Model Studio were retained. Updated checks: 26 Python, 7 Markdown-renderer and 3 quota-view tests.
- User requested full PPT, LaTeX report, Model Studio repair/chatbot UI and simple group-chat refinement, then asked to continue tomorrow and clean up. Recorded these as next tasks; no new work on them started during cleanup. Model Studio's new reported failure has not been reproduced.
- Claude reported reaching its usage limit. Codex announced takeover of the pending demo and final MMM-ML export/push, preserving the single-publisher convention.

- AI-GroupChat final inline-figure integration was accepted by GitHub as `d38be98`; earlier UI/usage bundle is `6665365`. Local runtime figures/transcripts/session selectors remain excluded.
