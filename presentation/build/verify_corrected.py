"""Checks the corrected deck against the 9 Nov 2026 audit (codex/presentation-audit, 118fdf5).

Usage: python verify_corrected.py <corrected.pptx> <slide_text.md> <out.json>
slide_text.md is the output of the pptx skill's slide_text.py (slide text, tables, chart data, notes).
"""
import hashlib, io, json, re, sys, zipfile
from PIL import Image, ImageSequence

pptx, md, out = sys.argv[1:4]
text = open(md, encoding="utf-8").read()
parts = re.split(r"<!-- Slide number: (\d+) -->", text)
slides = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
low = text.lower()

def has(s): return s.lower() in low
def slide_has(n, s): return s.lower() in slides[n].lower()

checks = {
    "slide_count_20": len(slides) == 20,
    "notes_on_every_slide": all("### notes" in v.lower() or "notes:" in v.lower() for v in slides.values()),
    # required corrections
    "1_lambda_zero_visible_slides_4_12_13_14_19": all(("λ = 0" in slides[n]) for n in (4, 12, 13, 14, 19)),
    "1_no_physics_benefit_statement": slide_has(12, "No accuracy benefit from physics is shown") and slide_has(13, "do not show an accuracy benefit"),
    "2_porosity_mapping_slides_9_14_18": slide_has(9, "φ = 1 − ρ/2700") and slide_has(14, "φ = 1 − ρ/2700") and slide_has(18, "φ = 1 − ρ/2700"),
    "2_case_values_and_study_point": slide_has(18, "0, 3 and 7.85") and slide_has(18, "2592") and slide_has(3, "2592"),
    "2_old_fixed_4pct_claim_removed": not has("fixed at 4 % as an assumption, not a model input"),
    "3_single_peak_not_validation": slide_has(8, "does not validate the material law") and slide_has(19, "does not validate"),
    "3_old_matches_ansys_title_removed": not has("our curve matches Ansys") and not has("Plasticity halves the peak"),
    "3_ratio_1_86": slide_has(8, "1.86×") and not has("1.85×"),
    "4_crack_model_route": slide_has(3, "crack-opening stress") and slide_has(17, "crack geometry and orientation"),
    "4_not_fatigue_criterion": slide_has(3, "not a fatigue-life or airworthiness criterion") and slide_has(17, "not a fatigue-life or airworthiness criterion"),
    "4_no_peak_vm_into_formula": not has("stress at the critical location (Ansys)"),
    "5_fast_rate_claim_fixed": not has("best groups are the fast rates") and slide_has(16, "100 °C · 10⁻³ is 0.45"),
    "6_group_mean_6_23": not re.search(r"6\.24\b", text) and slide_has(12, "6.23") and slide_has(13, "6.23"),
    "6_selection_bias_disclosed": slide_has(12, "used to select") and slide_has(13, "used in selection"),
    "7_e11_vs_eps_p_defined": slide_has(14, "total axial strain (not equivalent plastic strain)") and slide_has(6, "total axial strain E11"),
    "7_eq_variables_defined": all(slide_has(14, s) for s in ("ε̇₀ = 10⁻⁵", "T* = max[(T − 30)/(600 − 30), 0]", "G₀ = 25 300")),
    "8_parameter_count": slide_has(14, "385 network weights and biases + 7 JC constants = 392") and slide_has(14, "1 960"),
    "9_deployment_status": slide_has(17, "EXISTS") and slide_has(17, "material-card writer") ,
    "removed_wrong_model_studio_claim": not has("still serves an earlier MLP"),
    "removed_recipe_attribution": not has("strong weight decay, log-space output"),
    "removed_never_seen_tested_once": not any(has(s) for s in ("never seen", "tested once", "scored once")),
    "no_other_models": not any(has(s) for s in ("ensemble", " pca", "gaussian process", "5 networks")),
    # preserved verified results
    "kept_0_4386": slide_has(15, "0.4386"), "kept_r2": slide_has(15, "0.9995"),
    "kept_94_9": slide_has(15, "94.9 %"), "kept_37_of_37": slide_has(15, "37 / 37"),
    "kept_not_blind": slide_has(15, "Not a blind test"), "kept_inferred_units": slide_has(9, "inferred"),
    "kept_ansys_peaks": all(slide_has(7, v) for v in ("595.27", "320.79", "323.81")),
}

z = zipfile.ZipFile(pptx)
gifs = {}
for name in z.namelist():
    if name.endswith(".gif"):
        im = Image.open(io.BytesIO(z.read(name)))
        frames = [f.info.get("duration", 0) for f in ImageSequence.Iterator(im)]
        gifs[name] = {"frames": len(frames), "total_ms": sum(frames), "loop": im.info.get("loop"), "bytes": len(z.read(name))}
ct = z.read("[Content_Types].xml").decode()
checks["gifs_embedded_animated"] = len(gifs) == 2 and all(g["frames"] > 30 for g in gifs.values()) and "image/gif" in ct

res = {"pptx": pptx, "sha256": hashlib.sha256(open(pptx, "rb").read()).hexdigest(), "checks": checks,
       "all_pass": all(checks.values()), "gifs": gifs,
       "not_checked": ["Playback inside Microsoft PowerPoint Slide Show (no PowerPoint in this environment; GIF frames, timings and loop flag were checked from the embedded files)",
                       "Native PowerPoint layout: rendering was checked through LibreOffice; Calibri/Arial are metric-compatible (Carlito/Liberation)"]}
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in checks.items() if not v}, ensure_ascii=False) or "all pass", res["all_pass"])
