"""Turn a plain-English request into material conditions. Deterministic: no LLM, no network.

Understands, e.g.:
  "stress curve at 150 C and rate 1e-4"
  "compare 30, 100 and 200 °C at 1e-3 /s"
  "T=373 K, strain rate 0.0001, density 2619, G 24.5 GPa"
  "what is the stress at strain 0.05 for 100C?"
"""
import re

DEFAULTS = {"temperature": 30.0, "rate": 1e-4, "density": 2700.0, "G": 25300.0}
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def _nums(s):
    return [float(x) for x in re.findall(NUM, s)]


def parse(text):
    """Return {'intent', 'conditions': [dict, ...], 'strain_query', 'defaults_used', 'notes'}."""
    raw = text.strip()
    t = raw.lower().replace("°", " ").replace("×10^", "e").replace("x10^", "e")
    out = {"intent": "predict", "conditions": [], "strain_query": None, "defaults_used": [], "notes": []}

    if not t or re.fullmatch(r"(help|\?|hi|hello|hey|what can you do\??)[.!]?", t):
        out["intent"] = "help"
        return out
    if re.search(r"\b(range|limits?|valid|trained on|training data)\b", t) and not re.search(NUM, t):
        out["intent"] = "ranges"
        return out
    if re.search(r"\b(how (good|accurate)|accuracy|error|performance|tested)\b", t) and not re.search(NUM, t):
        out["intent"] = "accuracy"
        return out
    if re.search(r"\b(lift|c_?l\b|coefficient of lift|aerodynamic)", t):
        out["notes"].append("lift")
    if "porosity" in t or "porous" in t:
        out["notes"].append("porosity")

    # Strain query: "at strain 0.05" / "ε=0.05" / "5% strain"
    m = re.search(r"(?:strain|ε|eps(?:ilon)?)\s*(?:of|=|:|at)?\s*(" + NUM + r")\s*(%)?", t)
    if m and not re.search(r"strain\s*rate", t[m.start():m.end() + 6]):
        v = float(m.group(1)) / (100 if m.group(2) else 1)
        out["strain_query"] = v
    m = re.search(r"(" + NUM + r")\s*%\s*strain", t)
    if m:
        out["strain_query"] = float(m.group(1)) / 100

    temps = []
    # "30, 100 and 200 c" / "150c" / "150 deg c" / "373 k" / "t=150"
    for m in re.finditer(r"((?:" + NUM + r"\s*(?:,|and|vs\.?|versus|or|to)?\s*)+)\s*(?:deg(?:rees)?\s*)?"
                         r"(c|celsius|k|kelvin)\b", t):
        vals = _nums(m.group(1))
        kelvin = m.group(2) in ("k", "kelvin")
        temps += [v - 273.15 if kelvin else v for v in vals]
    m = re.search(r"\b(?:t|temp(?:erature)?)\s*(?:=|:|of|at)?\s*(" + NUM + r")", t)
    if m and not temps:
        temps.append(float(m.group(1)))

    rate = None
    m = re.search(r"(?:strain\s*)?rate\s*(?:=|:|of|at)?\s*(" + NUM + r")", t) or \
        re.search(r"(" + NUM + r")\s*(?:/\s*s|s\^?-1|per second)", t)
    if m:
        rate = float(m.group(1))

    density = None
    m = re.search(r"(?:density|rho|ρ)\s*(?:=|:|of)?\s*(" + NUM + r")", t)
    if m:
        density = float(m.group(1))
        if density < 10:  # g/cm3 -> kg/m3
            density *= 1000

    shear = None
    m = re.search(r"(?:\bg\b|shear\s*modulus|modulus)\s*(?:=|:|of)?\s*(" + NUM + r")\s*(gpa|mpa)?", t)
    if m:
        shear = float(m.group(1))
        if m.group(2) == "gpa" or shear < 1000:
            shear *= 1000

    if not temps:
        temps = [DEFAULTS["temperature"]]
        out["defaults_used"].append("temperature")
    if rate is None:
        rate = DEFAULTS["rate"]
        out["defaults_used"].append("rate")
    if density is None:
        density = DEFAULTS["density"]
        out["defaults_used"].append("density")
    if shear is None:
        shear = DEFAULTS["G"]
        out["defaults_used"].append("G")
    seen = []
    for T in temps:
        if T not in seen:
            seen.append(T)
    out["conditions"] = [{"temperature": T, "rate": rate, "density": density, "G": shear} for T in seen[:6]]
    if len(seen) > 6:
        out["notes"].append("too_many")
    return out
