# Room checkpoint — MMM-ML

Updated by Codex, 25 October 2026, approximately 14:39 UTC. Manual checkpoint; consume newer unread messages before acting. Agent mentions do not wake idle sessions. Read incoming authors chronologically; user instructions govern.

## Current user requests

- Detailed, easy personal model guide in LaTeX or Word; verify/improve the model.
- General native group-chat app: independent room per project, human/agent friendly, neutral theme, integrated terminals, efficient incremental context, substantial UI improvements and strong backend.
- Try **embedding Ghostty** (latest instruction supersedes the earlier separate-window preference). A separate Ghostty action may remain available; do not call xterm Ghostty.
- Highlight actual requests for user input/approval in the room. Avoid echoing stale notices after approval is resolved. Prompt detection is heuristic and must never auto-submit credentials or authorize actions.
- Put requested deliverables in `project files/`; publish completed code/docs to the existing private repos, retaining raw-data/runtime-chat/telemetry exclusions. No force-push.
- User explicitly assigned UI redesign to **Claude**, then restored equal-peer collaboration (no continuing orchestrator role). App desktop launcher is installed and points to the Electron app.
- Latest requests: selectable animated themes, agent task panel, .doc/.docx formatting repair, speed/storage efficiency, all-terminal input alerts, and checking both OpenCodes are working.

## Identities and ownership

| Work | Owner | Current handoff |
| --- | --- | --- |
| Native backend/main/preload/package/transport/engine integration; AI-GroupChat publication | Codex | `/home/sarvn/Documents/AI-GroupChat/native/`; do not edit concurrently |
| Native renderer UI redesign | Claude | `native/renderer/index.html`, `styles.css`, `polish.css`, required renderer.js wiring; retain functional IDs |
| Renderer functions / transcript export | OpenCode 2 (`opencode2`) | Actual initial implementer; Claude owns renderer.js now; OpenCode 2 owns self-contained export.js + script tag |
| Independent backend review | OpenCode 1 (`opencode`) | Read-only review requested; findings in separate `native/BACKEND_REVIEW.md`, no source edits |
| Guide formatting / themes / task panel | Gemini (`gemini`, Antigravity) | Repairing .doc/.docx and rendering; owns themes.js/css, agent-tasks.js/css, terminal-quote.js, checkpoint.py; not shared styles/layout |
| Model Studio, presentation and MMM-ML publication | Claude | Studio runtime integrated; presentation now reported 24 slides; final deck review remains |
| Source/model verification and runtime adapter | Codex | Complete evidence/scripts/tests listed below; original model/split preserved |

Two OpenCode instances initially shared `opencode` and collided on receipts. Both now have independent IDs/display names: **OpenCode 1** (`opencode`) and **OpenCode 2** (`opencode2`). Earlier shared-ID attribution is ambiguous; do not guess.

## Verified model facts and deliverables

Final Svm predictor: five 5–16–16–1 tanh query MLPs, 385 parameters each, alpha0.001, seeds0..4. Seed42 split36/37; 120 E11 queries per curve. Units remain inferred; no lift labels or verified porosity mapping/ANSYS integration. Earlier all-data exploration means the test set is not fully blind.

Codex checked 73 raw curves / 2,197,000 rows against cached interpolation: max difference0. Exact final reload and fresh same-environment frozen-config training reproduce all weights/predictions (25s, no warnings). Evidence: `reports/model_verification_20261025.json`, `reports/final_training_reproduction_20261025.json`. Test mean RMSE0.05908515; worst0.11330618 (45); training CV1.15826321; condition-holdout mean6.79360255; hot/slow23.52512868.

NumPy adapter `src/query_runtime.py`: 13 model/parser/runtime tests pass. Same predictions; local warm one-curve0.511→0.221ms, fresh process976→163ms; 73-case batch slower21.8 vs17.3ms. Benchmark is latency/file bytes, not memory/spend. Claude integrated it into Studio and corrected stale metrics/units. Guide worked example checked: E11 scaler mean0.0500499999999999, scale0.02902175956090894; nearest-grid stress99.63293075; interpolation at.05 gives99.41858716. Do not replace these with rounded array displays as a factual correction.

Guide factual/visual review addressed architecture, units, unsupported physical claims, code API and command fixes; current formatted PDF/Word files are in `project files/`. Latest presentation is reported24 slides; older15-slide export was caught and replaced. Claude reports private MMM-ML pushes including `cabc260` and a later24-slide update; verify actual latest commit/artifact before final delivery.

## Native app verification and remaining work

- Electron45 + integrated Ghostty WASM/Canvas desktop smoke PASSED, including actual paste→Unix PTY→Unicode→Ghostty buffer, empty-write guard, clipboard image→attachment-only post→decoded preview, rich table/chart, usage cards, two-project isolation/restoration, theme, join prompt and stop. Uses temporary projects/app state, no AI processes. Latest screenshot `/tmp/ai-groupchat-smoke-Wwed4K/desktop.png` inspected.
- Backend15 Python, bridge3 Node, watcher1 Node, terminal-attention1 Node and collaboration27 Python tests pass. Browser loopback test needs normal sandbox escalation; rerun passed. Windows PTY is **not implemented/tested**; macOS untested.
- Ghostty dependency is ghostty-web0.4.0; adapter guards observed empty-write RangeError, visibly labels xterm fallback. It is Ghostty WASM + Canvas, not native OpenGL/Metal; no speed/memory savings claimed from engine selection.
- Native attachment storage enforces file/count/size/path bounds and copies originals. Async imports now discard results if project switched. Usage uses shipped trusted adapters/cache; OpenCode 1/2 each confirmed distinct IDs, configured only in local ignored usage-sources.json. No invented costs/quotas or summed incomparable totals.
- Main-process filesystem watcher is tested but renderer watchRoom/room.changed hookup is still pending Claude confirmation. Wants delta reads + 20s fallback, no lost event during in-flight read.
- Cross-project native notification handler implemented by Codex: generic content only, bounded/cooldown, focus target event terminal.focus; Claude renderer switch/open hookup and real cross-project smoke pending. Existing prompt detection is heuristic. External independent terminals need explicit agent notices.
- Gemini agent-tasks.js initially used innerHTML with message-derived text; requested DOM/textContent fix before shipping and honest inferred-task/post-age labels (posting is not proof a model is running). Check actual source before calling fixed.
- Native README added, JSON export save filter fixed. AI-GroupChat commit/push remains pending final feature integration/tests and generic documentation. Keep runtime rooms/attachments/session selectors out of Git; no force push. BACKEND_REVIEW.md draft contains stale claims/literal shell debris; exclude or correct before publication.
- Guide Word formatting repair is currently Gemini's work. Earlier fact/visual review does not establish the replacement file has passed; inspect actual newly rendered pages. Preserve precise scaler/worked-example numbers above.

Room http://127.0.0.1:8765 · Model Studio http://127.0.0.1:8766. Runtime process IDs are not durable instructions. Source evidence/history: `context.md`, `tasks.md`, `logs.md`, `reports/` and subsequent unread messages.
