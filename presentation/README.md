# Slide deck

The project's full slide deck is **`Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx`** and its PDF (24 slides). The shorter submission deck below is cut from it. It is 16:9, with speaker notes on every slide, and is built by `build/build_corrected.js`.

The numbers on the finite-element slides (16–19), and the critical-flaw-length result on the objective, deployment, limits and conclusion slides, are read from `report/numbers.json`. The figures come from `figures/`.

**22 November 2026:** slides 1, 3, 4, 8, 15, 19 and 21–23 were brought up to date: the critical flaw length is now assessed (post-hoc, CL > 30 mm at the 35.9 kN capability-based limit load) rather than planned, the model-to-ANSYS coupling exists rather than being proposed, and the accuracy slide quotes MPa (units confirmed by the user). The deck still has 24 slides, so the slide selection in `scripts/make_submission_deck.py` is unchanged. The PDF was exported with LibreOffice on Linux, where the metric-compatible Carlito and Liberation Sans replace Calibri and Arial.

## Slides

**Submission deck (18 November 2026).** `scripts/make_submission_deck.py` writes `submission/Team8_Presentation_source.pptx`: cover, 15 content slides (2, 3, 5, 7, 9, 10, 12, 14, 15, 17–20, 22, 23 of the corrected deck, renumbered 1–15) and the thank-you slide. That file was imported into Canva and exported as `Team8_Presentation.pptx` / `.pdf`; the exports are part of the submission folders built by `scripts/build_submission.py` and are not committed.


| Section | Slides |
|---|---|
| Problem | Cover, problem statement, objective, life-cycle roadmap |
| CAD and Ansys | CAD model, loads and supports; the team's Ansys simulations (`source/Comparison Study - Final.wbpj`), their results and comparison |
| EDA | The dataset, curves and factor effects, data preparation |
| Model | Choosing the network; JC-PINN against a plain MLP (the one baseline); data modelling and training |
| Evaluate | Test results; results by condition and limits |
| Deploy | 16: the locked model as an ANSYS user material (USERMAT) and its checks · 17: the bracket with the JC-PINN, and the density-only porosity comparison · 18: porosity with G coupled by the assumed G = 25300 (1 − φ) (decision D5) · 19: the mesh study (the response after yield is mesh dependent) · 20: what exists and what is planned |
| Limits | Limits and open questions, conclusion, thank you |

## Wording and limits on the slides

- **Units:** confirmed by the user (no generator documentation).
- **Density:** stands for porosity.
- **Validity:** nothing is validated above 200 °C.
- **Bracket forces:** mesh dependent after yield, so not a converged strength.
- **Validation:** none is experimental.

## Inputs

| Path | What it is |
|---|---|
| `assets/` | Images and animations placed on the slides |
| `source/Comparison Study - Final.wbpj` | The team's Ansys comparison project (elastic, built-in JC, user-defined JC); only the project file is kept |
| `source/results/` | The team's Ansys contour screenshots |
| `source/model/` | Model outputs used by `build/data_figures.py` |
| `verification_corrected/` | The 9 November check of the deck against the locked model (20-slide version, before the finite-element slides were added) |

## Rebuild

1. Regenerate the inputs (diagrams, result crops, data figures):

```bash
pip install gmsh==4.15.2 matplotlib numpy pillow
```
```bash
python presentation/build/extract_planform.py presentation/build/planform.json
```
```bash
python presentation/build/diagrams.py presentation/build/planform.json
```
```bash
python presentation/build/crop_results.py
```
```bash
python presentation/build/data_figures.py presentation/build/planform.json
```

2. Build the deck. `<pptx skill dir>` is a folder containing `scripts/apply_theme.js`:

```bash
NODE_PATH=<dir containing node_modules> node presentation/build/build_corrected.js <pptx skill dir>
```

3. Export the PDF:

```bash
soffice --headless --convert-to pdf --outdir presentation "presentation/Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx"
```

Run `python scripts/write_latex_numbers.py` first whenever a saved result changes, so the deck reads current numbers.

Style: Calibri throughout, with Carlito (metric-compatible) inside the diagram images. Colours are navy `14213D`, steel `2F5D8A` and signal orange `E8590C` (loads and porosity).
