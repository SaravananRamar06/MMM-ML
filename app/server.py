"""Local chatbot for the AlSi10Mg stress–strain model. No LLM, no network calls.

Start:  .venv/bin/python app/server.py        then open http://127.0.0.1:8766
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]

import joblib  # noqa: E402
import numpy as np  # noqa: E402

from data import STRAIN_GRID  # noqa: E402  (also needed so joblib can unpickle src.models classes)
from nlu import parse  # noqa: E402
from predict import warnings_for  # noqa: E402

CONFIG = json.loads((HERE / "config.json").read_text())
MODELS = {m["key"]: {**m, "model": joblib.load(ROOT / m["artifact"])} for m in CONFIG["models"]}
PRIMARY = CONFIG["primary"]
PORT = int(os.environ.get("MODEL_CHAT_PORT", "8766"))

HELP = """I predict **stress–strain curves** for the professor's AlSi10Mg simulations.

Try:
- `stress curve at 150 C, rate 1e-4`
- `compare 30, 100 and 200 C at 1e-3 /s`
- `stress at 5% strain for 100C, density 2619, G 24541`
- `what ranges are valid?` · `how accurate is it?`

**Inputs:** temperature (°C or K), strain rate (/s), density (kg/m³), shear modulus G (MPa or GPa).
Anything you leave out uses the dense reference: 30 °C, 1e-4 /s, 2700 kg/m³, 25,300 MPa."""

RANGES = """The data has **73 available simulation cases**; these models were **fitted on the 36-case training half**, at these levels:

| Input | Range |
|---|---|
| Temperature | 30, 100, 200 °C (no 300 °C data) |
| Strain rate | 1e-5, 1e-4, 1e-3 /s |
| Density | 2488–2700 kg/m³ (almost no effect on stress) |
| G | 23,314–25,300 MPa |
| Strain | 0.0002–0.0999 |

Between these levels the model interpolates. Outside them it extrapolates, and I'll warn you."""


def accuracy_text():
    rows = "\n".join(f"| {m['label']} | {m['test_rmse']} | {m['unseen_rmse']} |" for m in MODELS.values())
    return ("Error per curve, RMSE in MPa (unit provisional):\n\n| Model | 37 test cases | unseen T/rate condition |\n|---|---|---|\n"
            + rows + "\n\nTest cases were not used to fit these models, but they did influence earlier model "
            "choices, so the test set is not fully blind. Errors grow at 200 °C, and 200 °C / 1e-5 is weakest (~23 MPa).")


def predict(cond):
    x = np.array([[cond["temperature"], np.log10(cond["rate"]), cond["density"], cond["G"]]])
    return {k: m["model"].predict(x)[0] for k, m in MODELS.items()}


def answer(text):
    p = parse(text)
    if p["intent"] == "help":
        return {"reply": HELP}
    if p["intent"] == "ranges":
        return {"reply": RANGES}
    if p["intent"] == "accuracy":
        return {"reply": accuracy_text()}
    if "lift" in p["notes"]:
        return {"reply": "I can't predict **coefficient of lift**. The supplied data has no lift values, and its "
                         "curves have no elastic segment (G is only a supplied input), so no model can learn "
                         "porosity → C_L from it. "
                         "That needs aerodynamic data or an agreed physics calculation (questionnaire Q01–Q04). "
                         "I can predict the stress–strain curve for a material condition."}
    for c in p["conditions"]:
        if c["rate"] <= 0:
            return {"reply": "The strain rate must be positive, e.g. `rate 1e-4`."}

    curves, warn, lines = [], [], []
    for c in p["conditions"]:
        pr = predict(c)
        lab = f"{c['temperature']:g} °C, {c['rate']:g}/s"
        for k, y in pr.items():
            curves.append({"label": lab + ("" if k == PRIMARY else f", {MODELS[k]['short']}"),
                           "model": k, "primary": k == PRIMARY, "strain": STRAIN_GRID.round(5).tolist(),
                           "stress": np.round(y, 3).tolist()})
        y = pr[PRIMARY]
        if p["strain_query"] is not None:
            e = min(max(p["strain_query"], STRAIN_GRID[0]), STRAIN_GRID[-1])
            if abs(e - p["strain_query"]) > 1e-12:
                w = (f"Strain {p['strain_query']:g} is outside the modelled range "
                     f"{STRAIN_GRID[0]:g}–{STRAIN_GRID[-1]:g}; showing the value at {e:.4f} instead.")
                if w not in warn:
                    warn.append(w)
            v = {k: float(np.interp(e, STRAIN_GRID, yy)) for k, yy in pr.items()}
            lines.append(f"| {lab} | ε = {e:.4f} | " + " | ".join(f"{v[k]:.1f}" for k in MODELS) + " |")
        else:
            lines.append(f"| {lab} | {y[0]:.1f} | {np.interp(0.05, STRAIN_GRID, y):.1f} | {y[-1]:.1f} |")
        if min(float(yy.min()) for yy in pr.values()) < 0:
            w = (f"At {lab} a model predicts negative stress, which is physically impossible; "
                 "this condition is beyond what the models can represent.")
            warn.append(w)
        for w in warnings_for(c["temperature"], np.log10(c["rate"]), c["density"], c["G"]):
            if w not in warn:
                warn.append(w)

    if p["strain_query"] is not None:
        head = "| Condition | Strain | " + " | ".join(m["label"] for m in MODELS.values()) + " |\n|---|---|" + "---|" * len(MODELS)
    else:
        head = (f"Predicted **{CONFIG['target_label']}** ({MODELS[PRIMARY]['label']}), MPa:\n\n"
                "| Condition | start (ε≈0) | ε = 0.05 | end (ε = 0.1) |\n|---|---|---|---|")
    reply = head + "\n" + "\n".join(lines)
    if p["defaults_used"]:
        reply += "\n\n_Defaults used for: " + ", ".join(p["defaults_used"]) + "._"
    if "porosity" in p["notes"]:
        reply += ("\n\n_Porosity isn't a direct input: the porosity ↔ density/G mapping is unconfirmed. "
                  "Give density and G values instead._")
    if len(MODELS) > 1 and curves:
        reply += "\n\nThe dashed line is the comparison model; where the two lines disagree, trust both less."
    return {"reply": reply, "curves": curves, "warnings": warn}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/health":
            self._send(200, json.dumps({"ok": True, "config_status": CONFIG.get("status"), "primary": PRIMARY,
                                        "models": {k: m["artifact"] for k, m in MODELS.items()},
                                        "parser": "deterministic rules (app/nlu.py); no LLM or network calls"}),
                       "application/json")
        elif self.path == "/api/info":
            self._send(200, json.dumps({"target": CONFIG["target_label"], "models": [
                {k: m[k] for k in ("key", "label", "short", "test_rmse", "unseen_rmse")} for m in MODELS.values()],
                "primary": PRIMARY}), "application/json")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/chat" or self.headers.get("Host") not in (f"127.0.0.1:{PORT}", f"localhost:{PORT}"):
            return self._send(403, "forbidden", "text/plain")
        n = int(self.headers.get("Content-Length") or 0)
        if n > 4000:
            return self._send(413, "too long", "text/plain")
        try:
            text = json.loads(self.rfile.read(n) or b"{}").get("text", "")
            self._send(200, json.dumps(answer(str(text)[:500])), "application/json")
        except Exception as exc:  # keep the chat alive; report the problem in the reply
            self._send(200, json.dumps({"reply": f"Sorry, I couldn't handle that ({type(exc).__name__}). Try `help`."}),
                       "application/json")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Model chat on http://127.0.0.1:{PORT}  (Ctrl+C to stop)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
