# Slide deck

The project has one slide deck: **`Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx`** and its PDF. It is 16:9, with speaker notes on every slide, and is built by `build/build_corrected.js`.

The numbers on the finite-element slides (16–18) are read from `report/numbers.json`. Their figures come from `figures/`.

## Slides

| Section | Slides |
|---|---|
| Problem | Cover, problem statement, objective, life-cycle roadmap |
| CAD and Ansys | CAD model, loads and supports; the team's Ansys simulations (`source/Comparison Study - Final.wbpj`), their results and comparison |
| EDA | The dataset, curves and factor effects, data preparation |
| Model | Choosing the network; JC-PINN against a plain MLP (the one baseline); data modelling and training |
| Evaluate | Test results; results by condition and limits |
| Deploy | 16: the locked model as an ANSYS user material (USERMAT) and its checks · 17: the bracket with the JC-PINN, and the density-only porosity comparison · 18: the mesh study (the response after yield is mesh dependent) · 19: what exists and what is planned |
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
