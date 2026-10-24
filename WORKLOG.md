# Work log

What was done on this project, in order, and by whom. Written in plain English; the
technical detail is in [`reports/`](reports) and the project notes in [`docs/`](docs).

Participants: the student (project owner) and three AI coding agents working in a shared local chat
room: **Claude** (Anthropic), **Codex** (OpenAI) and, from the end of 24 October, **Gemini** (Google).

## 24 October 2026

### Understanding the project
- **Codex** read the brief, the submitted presentation and the professor's data, then wrote the
  project notes (`docs/`): context, decisions, open questions and a 100-question questionnaire.
- The student confirmed that **CL means coefficient of lift**. The submitted deck had treated it as
  critical flaw length, and had used synthetic porous cells instead of the professor's data.
- **Codex** researched model options and recommended a small "query" neural network.

### Independent analysis
- **Claude** analysed all 73 simulation files without relying on that recommendation and found:
  - Temperature and strain rate drive the stress curve.
  - Shear modulus matters a little.
  - Density barely matters.
  - The curves have no elastic part.
  - One run (case 60) collapses irregularly.
- **Claude** compared five model types. A random 50/50 split turned out to be an easy test, so it
  added a harder one: hiding a whole temperature/rate combination.

### Building and checking the models
- **Claude** built the pipeline (`src/`): data loading, the saved 36/37 split, three models, and
  evaluation with figures.
- **Codex** reviewed Claude's work and caught real problems. Claude fixed all of them:
  - **GP uncertainty:** Claude had claimed the Gaussian-process uncertainty would flag extrapolation.
    Claude tested it, and it failed (0 % coverage at 200 °C), so the claim was withdrawn.
  - **Selection exposure:** model settings had been chosen while looking at all cases. Claude added
    training-only selection (`src/select_settings.py`) and disclosed the earlier exposure.
  - **Wording and saved artifacts:** wording and saved-model alignment were corrected.
- **Codex** independently reloaded every saved model and recomputed every metric; all matched.

### Choosing the final model together
- The student asked the agents to collaborate, not compete. **Claude** built a shared scorer
  (`src/score.py`) with a selection rule fixed before the last results were seen, and a one-time
  lock on the test set.
- **Codex** built a curve-shape network (`src/pca_mlp.py`); Claude reviewed it.
- **Results:**
  - The Gaussian process interpolates best.
  - The query neural network is the best network, and the best on unseen conditions.
  - Codex's network didn't help on this data.
  - The course asks for a neural network, so both agreed the **query MLP** is the final model.
- **Final test score:** 0.059 MPa mean error per curve on the 37 held-out cases, scored once
  (`runs/score/final_Svm/`).

### Making it usable
- **Claude** built **Model Studio** (`app/`): a local chat page where you ask for curves in plain
  English. It runs offline using fixed text rules, not an AI model, and warns outside the trained
  range.
- **Codex** ran real requests through it as an end-to-end check, and Claude applied its wording fixes.

### Publishing
- **Claude** published this repository with a beginner-friendly README. It checked the repo from a
  fresh clone and scanned it for secrets. The professor's raw data was left out on purpose.
- **Claude** found and corrected its own mistake: the "one-level" factor-effect numbers had included
  two-level jumps (`src/factor_effects.py` now computes them properly).
- **Codex** published the group-chat app to its own repository, AI-GroupChat. **Claude** added a
  participant registry so more people and agents can join with one command, and restyled the room
  for readability.
- **Gemini** joined the room through that registry.

### Corrected presentation
- **Claude** built a new 15-slide deck from the real results, in the style of the first deck.
  Every number is listed with its source in [`reports/presentation/numbers.md`](reports/presentation/numbers.md),
  for Codex to fact-check.

## Still open
- **Questions for the professor:** where coefficient-of-lift values should come from, what porosity
  means in the data, the units, and what "two models" counts (questionnaire Q01–Q04, Q08).
- **Codex's fact-check of the deck**, then any corrections.
- **Ideas not yet started:**
  - a viva preparation pack (offered by Gemini);
  - a shear-modulus sensitivity study;
  - an ANSYS link, once the stress/strain definitions are confirmed.

## Independent demo check and next session

Codex reloaded the final saved model, reproduced all 37 archived predictions exactly, and independently checked case 42 (curve RMSE 0.106146). `reports/check_demo_case.py` generates a curve/residual figure. The demo's point display now interpolates to exactly strain 0.05. See `reports/demo-verification.md` for precise numbers and validation limits. No model was retrained.

The user requested stopping for the day. Next: full PowerPoint, LaTeX report, reproduce the reported Model Studio problem, and improve chatbot/group-chat usability without over-engineering. The latest handoff and collaboration checkpoint are included under `docs/`.
