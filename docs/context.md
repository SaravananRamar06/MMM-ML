# Current project context

**2 November 2026 - Current direction:** user selected the exact MLP prediction equation, then requested "test this". A fresh single 385-parameter MLP test is running with fixed 36/37 cases, training-only alpha selection and nested condition holdouts. This supersedes the MLP/PINN comparison request. See single-mlp-colab.md; no physical governing law is claimed.


**31 October 2026 - Effective-equation checks completed:** user selected an effective law and authorized using only the 36 training cases. Both tested exponential families fail prospective case-CV error limits (mean/worst normalized errors 5.79%/54.28% and 6.68%/58.28%). No equation is frozen for PINN use. See effective-equation-check.md, the physics-only notebook and reports/effective_equation_20261031/. The 37 test histories were excluded; no new neural network was created. Evm matches accumulated stress work divided by Svm numerically, not conventional accumulated plastic strain.

**31 October 2026 — Current requested plan:** compare MLP and PINN in Colab,
with the governing constitutive equation established before creating either
model. This supersedes the earlier one-network proposal below. User confirms
all available files are supplied; no VPSC inputs/run logs are available. Work
from the outputs and primary literature, labelling any selected constitutive
law as a hypothesis until qualified. The VPSC-like format is an investigative
lead, not verified provenance. See `mlp-pinn-colab-plan.md` for the physics-first
sequence and proposed common PyTorch implementation. Effective-equation calibration is now documented above; fixed assumed
phi=0.04 is retained.

**Latest user correction — 27 October 2026: CL = critical flaw length**, the largest pore or defect the AlSi10Mg bracket can carry at its design stress before fracture (linear-elastic estimate a_c = (1/π)(K_IC / Yσ)²). It is **not** the aerodynamic coefficient of lift. This overrides the 24 October "coefficient of lift" correction below; lift-based statements in older sections are kept only as history. The user also stated that both Ansys analyses (`Elastic.wbpj` here and the explicit Johnson–Cook bracket run in the separate `MMM-ML Project` folder) are their own work.

**31 October 2026 — Colab planning:** user requested a fresh notebook from the
professor data and selected scikit-learn, one neural network, and `E11 -> Svm`.
The proposed single-network rebuild is not implemented. User then asked about
adding porosity later; this is a future option. Density-derived phi requires
confirmed density/reference definitions and adds no independent information;
learning a separate phi effect requires paired response data. See the new
material-model section in `porosity-workflow.md`. Existing artifacts and split
are preserved; physical mappings remain unconfirmed.

**31 October 2026 — User-selected assumption:** use fixed nominal porosity
`phi = 0.04` (4%) for the planned study. This is an assumed study condition,
not a measured per-case label for the 73 histories. Record it in
`configs/study_assumptions.json` and future notebook metadata; retain the
five-input MLP because a constant feature cannot identify porosity dependence.
Density/G relations and source-history applicability remain unresolved.

**Latest verified state — 25 October 2026, 17:30 UTC:** the user requested a completed-work review, a team-voice README without contribution credits, a fresh model retest and a simple first-person model guide. `README.md` and `README.github.md` now match. New deliverables: `project files/My model explained.md`, its printable HTML version, and `project files/Model test results.md`. Detailed existing guides and fitted artifacts were preserved.

**Fresh retest:** `reports/retests/20261025T172218Z/results.json` records source/cache equality for 73 histories and 2,197,000 rows; mean test curve RMSE 0.05908515170863245, median 0.05056665519928898, worst 0.11330617910816165 (case 45), mean MAE 0.04899859206569091. A separate frozen-settings fit took 17.26 seconds and exactly reproduced every weight and prediction without warnings. NumPy predictions also match exactly. All 13 unit and 3 live Studio tests passed. The initial live attempt hit sandbox restrictions; Studio was subsequently found stopped, started and successfully checked. All four delivered artifact hashes remain unchanged. This is same-data/local-environment reproducibility, not a new blind or physical validation. Saved condition-holdout diagnostics were checked for aggregation, not rerun.

**Communication preference:** the user explicitly requested input questions in the group chat. No clarification is needed to complete the current documentation. Use the separate AI-GroupChat backend CLI; app migration/publication remains with its current room owner. This latest section supersedes older task ownership and stale runtime/status snapshots below.

**25 October active work:** user requests a detailed accessible LaTeX/doc model guide, verification/improvement, and research/build of a general native app with one independent group chat per project, neutral theme and backend terminals. Gemini owns the guide; the original OpenCode instance (`opencode`) owns native-app research/prototype. A second existing OpenCode terminal is registered as `opencode2` / OpenCode 2; the user confirmed naming it. Do not conflate their messages/read receipts. Codex owns new verification/runtime files; historical Claude-owned app files await handoff.

**New verification evidence:** `reports/model_verification_20261025.json` confirms all 73 raw curves (2,197,000 rows) reproduce cached data exactly, the documented case split, training-only scaler statistics, and exact final artifact reload. `reports/final_training_reproduction_20261025.json` records a fresh same-environment fit of the frozen five-network settings/seeds reproducing every weight and prediction exactly in 25 s without warnings. No new accuracy-selection experiment occurred. Training CV mean RMSE is 1.15826321 and condition-holdout mean is 6.79360255 (hot/slow 23.52512868), in inferred source stress units; final test mean remains 0.05908515. Studio's displayed unseen-condition figure was subsequently corrected to 6.79.

**Measured inference option:** new `src/query_runtime.py` exports identical float64 weights to a pickle-free NumPy NPZ, with 13 model/parser/runtime tests passing. Local single-curve median 0.511 -> 0.221 ms; fresh process/import/load/inference 976 -> 163 ms; 73-case batch was slower (21.8 vs 17.3 ms). Evidence in `reports/query_runtime_benchmark_20261025.json`. Integrated into Model Studio by Claude on 25 Oct (joblib fallback); no universal speedup or accuracy improvement claimed.

**25 October 2026:** user resumed Codex room monitoring and requested adding their existing OpenCode terminal session. OpenCode is registered as agent `opencode` in the live MMM-ML room; the running server's participant API confirms registration. Its first post is still required to establish participation. No usage provider or model invocation was added.

Last updated: **2026-10-24**, Asia/Kolkata.

## Latest collaboration state — overrides earlier implementation-status snapshots

**Current checkpoint, 24 October 2026:** the material model is implemented and selected. Final Svm predictor: five independently initialised 5–16–16–1 tanh query MLPs averaged; alpha 0.001, 385 parameters each. It maps `(T, log10(rate), density, G, E11)` to Svm, using 120 equally weighted strain queries per curve. `data/split.json` fixes seed 42, 36 training / 37 test cases. `runs/score/final_Svm/` holds the model, predictions, and metrics. Codex directly reloaded the final artifact and reproduced all 37 saved predictions with maximum absolute difference 0.0, then independently recomputed the saved curve RMSEs: mean 0.05908515, worst 0.11330618 (case 45), in inferred stress units. Earlier all-data exploration means this is not an untouched holdout. Condition-holdout results are much worse; no critical-flaw-length (CL) predictor or experimental validation is established.

- The bounded PCA-coefficient MLP comparison was implemented/tested and rejected on the saved training-side scores. PCA/GP remains a non-neural interpolation reference.
- Model Studio runs locally at `http://127.0.0.1:8766`. It uses a deterministic parser and the final saved model. Codex's three live API/inference checks passed; it is not an LLM chat service.
- User authorised publishing both private repositories: [MMM-ML](https://github.com/SaravananRamar06/MMM-ML) and [AI-GroupChat](https://github.com/SaravananRamar06/AI-GroupChat). Claude publishes MMM-ML; Codex publishes AI-GroupChat. Raw data, old submissions/handoffs, runtime messages, and telemetry are excluded from the curated exports.
- The shared room has four participants: user, Codex, Claude, and **Gemini**. Gemini is the user's existing **Antigravity/agy** coding-agent session, not a new Gemini CLI process. Its displayed name and ID stay Gemini / `gemini`. Gemini has actually posted and independently reviewed presentation claims.
- Current room scope: equal chronological attention to all participants, active-session polling, local usage panels with honest telemetry scopes, and a reusable dashboard. Claude owns current UI CSS/HTML changes and desktop launcher; Codex owns shared server/provider integration and chat-repo publishing. Gemini’s adapter is now reviewed, registered, explicitly session-selected in ignored local configuration, and available through the live HTTP API alongside Codex/Claude. Only Codex supplies logged quota snapshots in the currently checked sources; missing quotas are not zero or unlimited. Avoid concurrent edits without a handoff. Do not rely on historical retained process/session IDs below.
- User prioritises visual quality and clearer agent outputs; Claude reports a Calm/Expressive switch, command palette, mentions, output enrichment, and desktop launcher. Codex has not visually verified those latest changes or launched new agent sessions. Follow-up colour changes are in progress.
- Corrected presentation is a draft under review in `reports/presentation/`. Codex's `codex-fact-check.md` verifies saved aggregates and lists remaining wording/rounding changes; Gemini's `gemini-review.md` supplies a separate review. Claude owns the visual deck. Final visual corrections and submission packaging remain pending.

**Publication checkpoint, 16:16 UTC:** AI-GroupChat commit `6665365` was accepted by GitHub; the checkout is clean. Includes Claude’s final frozen UI, Gemini telemetry, quota snapshot timestamps/reset-passed semantics, safe emphasis/numbering fixes, and design research. Final checks: 25 Python and 9 JS tests; Codex inspected the after-layout screenshot. User confirmed the desktop shortcut successfully opens Claude, Codex and agy. Claude reports MMM-ML latest commit `5df212a`, including final slide text and UI-check artifacts.

Earlier bullets and sections below are historical snapshots; the checkpoint above supersedes their “not implemented / selection open” statements.

- Codex has independently reloaded all four selected material-model artifacts and reproduced their saved 37-case predictions and mean/median/worst RMSE values. See `reports/codex-selected-model-check.md` and its reproducible check script. This verifies inference/metric consistency, not independent fitting or blind/physical validation. Final target/model selection remains open.
- User requested continued chat monitoring and dark mode, then superseded their initial user-priority request with **equal attention to the user and Claude**. Codex reads incoming messages chronologically during active, bounded waits and replies in the shared room. The user's instructions retain their normal authority.
- Dark/light mode, browser-persisted preference, and explicit per-agent read acknowledgements are implemented. The dashboard was restarted in retained server session 27022; 12 tests and live HTTP checks pass. Browser rendering remains unverified in this tool session.
- Codex has now read both saved metrics JSONs, confirmed fitted-model/prediction artifacts exist, and answered the room's training-progress question. Both SCAU11 and Svm runs are complete as saved; metrics are exploratory, not independently reproduced fits. Later training-only selection does not undo earlier holdout exposure.
- User requested a comprehensive questionnaire: [project-questionnaire.md](project-questionnaire.md) has 100 questions with 12 priorities and confirmed facts prefilled. User answers are pending.
- The local dashboard is running at `http://127.0.0.1:8765`; [COLLABORATION.md](COLLABORATION.md) explains access, CLI posting, persistence, and the invitation to Claude. Agents read and reply during active turns; mentions do not wake them.
- User assigned Codex only its own usage panel, saying Claude will add its panel. Codex telemetry and its scope/caching/limit caveats are implemented. Claude's independent extension interface is in `collaboration/CLAUDE_USAGE_EXTENSION.md`.
- Claude has actually posted in the shared room. It reports owning `src/`, `data/`, `runs/`, `figures/`, and `.venv/`, plus preliminary experiments. Codex confirmed implementation files, run directories, and `data/split.json` with 36 train and 37 test cases exist. Its modelling results remain reported, not independently reproduced by Codex.
- Claude reports using `SCAU11` while the research recommendation uses `Svm`; align targets and units before comparing metrics. Existing experiments mean the project must no longer be described as having no implementation or an entirely uninspected holdout.
- Codex acknowledged ownership and requested Claude's modelling findings in `reports/claude-model-recommendation.md` before merging shared documents. Claude may own `collaboration/claude_usage.py` without changing Codex's provider/shared UI.
- Six room/provider tests and live HTTP/API checks pass; visual rendering was not verified because no browser was available. An attempt to open the dashboard through the browser tool returned `Browser is not available: iab`. The user can open the local URL directly.

**Superseded 27 October 2026:** on 24 October the user said CL = coefficient of lift, not critical flaw length. The user has since reversed this: CL = critical flaw length (see the top of this file).

## Evidence labels

- **Confirmed:** explicitly stated by the user in this conversation.
- **Observed:** read directly from local files; this does not establish the scientific validity of their contents.
- **Historical:** claims in earlier Claude-generated records or the submitted presentation; not reproduced here.
- **Proposed:** a possible method or working interpretation, not an approved requirement.

## Confirmed purpose and requirements

- College project course: Multiscale Modelling of Materials using Machine Learning.
- Four teammates; the user handles ML and another teammate handles ANSYS. The user reports that the other two have not contributed so far.
- Professor explicitly identified the supplied material as AlSi10Mg.
- Professor supplied the simulation dataset for material modelling; it is not specific to the wing rib bracket geometry.
- Intended project functionality includes **both**:
  1. Material conditions to a stress–strain curve.
  2. Porosity to **critical flaw length, CL**, with the material-to-bracket coupling and fracture inputs (flaw geometry, K_IC) still unresolved.
- CL versus porosity arose from discussion with the professor, who recorded the topic in his notebook. The user briefly redefined CL as coefficient of lift on 24 October, then confirmed on 27 October that CL is critical flaw length. The fracture target is current; the first deck's specific porous-cell method and numbers remain unverified.
- Professor approved the topic only; the presentation's method and formula were not specifically approved.
- Professor said to determine which neural-network type to use. The user recalls a maximum of two models, but is uncertain about the exact limit.
- Professor requested random selection of half the simulation cases for training and half for testing.
- User confirms the folder is complete as supplied, despite missing outputs relative to its matrix. Do not assume extraction failed.
- A working trained model, report, presentation, and viva are required. Exact final deadline is pending, described as next month on 2026-10-24.
- User introduced the phrase "first principles" hoping to improve the result. It is not a professor-specified requirement.
- User is proficient with Python, new to ML, and plans to use AI-assisted coding. They expect to explain the concepts rather than code details.

## Submission and provenance

- `AM Porosity in a Wing Rib Bracket.pdf` is the actual submitted presentation (user confirmed).
- The user generated it using Claude without providing the professor's simulation dataset.
- The user has not downloaded or run the prior analysis code and cannot verify the numerical claims from personal execution.
- The PDF's provenance slide says the cells and bracket were solved in Python, **not ANSYS**. The existence of the statement is observed; its execution claim is unverified.
- User initially described the earlier submission as "only the ANSYS results." How this relates to the submitted PDF remains unclear; preserve both statements until clarified.
- Teammate's ANSYS work is reported at a broad level. Actual solved analyses, parameters, project files, and exported results have not been inspected here. User will supply further material later.
- The two legacy handoffs describe earlier Claude conversations. The longer one includes embedded solver, data-generation, fitting, and ANSYS macro code, with some sections explicitly described as "core" excerpts.
- Finding those excerpts establishes that code text is available; it does not establish completeness, successful execution, or correct physics.

## Observed local state

- Project root: `/home/sarvn/Documents/MMM-ML`.
- Original sources: one PDF, two historical Markdown handoffs, and `TEAM_8_extracted_results_set_1/`.
- Matrix: 108 cases, a four-temperature by three-rate by three-density by three-modulus design.
- Available results: 73 `STR_STR.OUT` files; 35 matrix cases have no output.
- Available temperatures: 30, 100, and 200 in the matrix's temperature convention. No 300-temperature outputs exist.
- Curves have 1,000, 10,000, or 100,000 rows. These are 73 simulation histories, not millions of independent material experiments.
- No standalone training scripts, trained models, raw historical RVE JSON results, CAD, or ANSYS project files were found during inspection.
- Project directory was not a Git repository when checked on 2026-10-24.

## Research state as of 2026-10-24

- [research.md](research.md) synthesises primary-source architecture/workflow research and a reproducible audit of all 73 histories. Audit script, JSON results, and detailed notes are in `research_notes/Neural networks for material curves/`.
- All entries are finite and `E11` increases in every case; the exact common measured interval is `[0.0001, 0.09999996]`. Case 60 has reversing `Evm`, so `E11 -> Svm` is the recommended initial operational column mapping.
- Research recommends a compact regularised query MLP first and a PCA-coefficient MLP only if training-side reconstruction supports it. This is not an observed accuracy result or approval of exact hyperparameters.
- All-data exploratory PCA has occurred; do not describe the future holdout as never inspected. Do not reuse this descriptive basis for training or treat variance retention as prediction accuracy.
- Proposed split is 36 training/37 test cases with seed 42 and three internal case folds. No split manifest, trained model, or training pipeline exists yet.
- Units, initial state, generating constitutive model, porosity mapping, and the material-to-CL (fracture) connection remain unresolved. Research did not validate old deck claims.

## Scientific gap

The supplied data has material conditions and stress/strain histories, but no explicit porosity labels, flaw sizes or fracture-toughness values. The relationship between material predictions, porosity and critical flaw length cannot come from this data alone: it needs the stress at the bracket's critical location and a fracture-mechanics model.

The first deck describes a separate synthetic porous-cell study used to fit a stress-concentration law, followed by a fracture-mechanics calculation. It targets the right quantity (critical flaw length) but did not use the professor's dataset, and its numbers have not been reproduced. Any reuse of its method needs independent checking.

## Historical claims to keep separate

- Deck: 27 porous cells plus a dense cell, fitted `K_t(phi)`, several regression comparisons, and bracket capacity falling about 28% at 4% porosity.
- Later handoff: capacity loss revised to about 36% after changes to homogenised properties. This is a reported revision, not a verified correction here.
- Historical material constants differ between the custom solver and ANSYS; quoted Young's modulus also differs (70 versus 76.6 GPa).
- Historical bracket restraints differ between the custom solver and ANSYS.
- The old files use CL for critical flaw length, which matches the current project target, and C_L0 for the Cockcroft–Latham damage constant, which is a different quantity. Do not conflate CL with C_L0.
- Old claims that closed forms extrapolate safely, 2D cells provide conservative bounds, or a solver is verified require independent assessment before reuse.

## Collaboration preferences

Ask focused questions that uncover missing context. Do useful independent work where answers are not required. Explain why target definitions, data splitting, model choices, and physical assumptions matter for the viva. Do not require the user to already know ML in order to make progress.

The user specifically requested architecture research and a documented conclusion before model creation, then asked for all project context to be retained in Markdown. `README.md` indexes the handoff and detailed research notes. The current stage is research completed and implementation pending, not a trained-model deliverable.

## Current Windows checkout verification — 26 October 2026
Fresh inference/artifact verification passed on Windows; 17 unit and 3 live tests pass after replacing test-only excluded-cache input dependencies with manifest inputs. Raw files and training caches are absent, so source processing and training could not be freshly reproduced. See latest docs/logs.md entry and parent outputs/model-review.md. Model Studio was started locally on port 8766.

## Professor data restored and verified — 26 October 2026
Raw professor histories are now present. Fresh source audit verifies all 73 source hashes, prepared held-out truth and both training scalers. This supersedes earlier absent-data status. A frozen Windows refit differs (test mean curve RMSE 0.112603 vs delivered 0.059085), so exact training reproduction is not established in this environment. Saved-artifact inference is exact. No porosity labels/definitions, bracket performance labels, flaw sizes or fracture-toughness data were supplied; full-purpose alignment remains incomplete. See latest logs entry.

## Porosity workflow software — 26 October 2026
New /workflow interface and CLI support declared porosity-to-material studies and comparison of supplied solver results, with evidence/range gates. Both STEP parts imported/measured successfully. 30 unit and 7 live API tests passed; browser checks passed. This is software preparation, not physical project completion: no solved bracket/wing model or new bracket/lift predictor exists. Required physical definitions remain pending from user; see configs/porosity_workflow.json and docs/porosity-workflow.md. (Its lift-coefficient path predates the 27 October CL correction.)
