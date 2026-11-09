# Presentation: Effect of Porosity on an AM Wing Rib Bracket

`Porosity in an AM Wing Rib Bracket.pptx` (14 slides, 16:9, speaker notes on every slide) and a PDF copy.
It replaces the October deck, which used a home-made Python solver, treated CL as lift in one version and
quoted unverified capacity-loss figures. None of that content is reused here.

| # | Slide | Rests on |
|---|---|---|
| 1 | Title | Team names and course |
| 2 | Problem statement | Laser powder-bed fusion porosity (general background) |
| 3 | Objective: CL(φ) | CL = critical flaw length (user, 27 Oct); φ = 4 % assumed (`configs/study_assumptions.json`) |
| 4 | Impact in service | Qualitative mechanics; the "about 2×" factor is the classical stress concentration for a round void |
| 5 | CAD model | `Rib Bracket.STEP` measured with gmsh: 231.5 × 230 × 40 mm, 778 cm³, Ø10 mm bore, two 50 × 40 mm mounting faces at x = 210 mm |
| 6 | Forces | Bore at x = 0, mounting faces at x = 210 mm, so R = F and M = F × 210 mm; arm tension/compression is a truss estimate |
| 7 | Why the upper half of the bore | The STEP bore is two 628 mm² half-faces; pin-bearing contact reasoning |
| 8 | Comparison Study set-up | `source/Comparison Study - Final.wbpj`: three Explicit Dynamics (AUTODYN) systems named Elastic, Built-in JC and User Defined JC, all using `Rib Bracket.STEP` |
| 9–11 | EL, JC-B, JC-U | Material property lists for AlSi10Mg - EL / JCB / JCU in the same `.wbpj` |
| 12 | Comparison | Capabilities of each material model, plus the results we expect |
| 13 | Results | Empty frames for the three Workbench contours and their peak values |
| 14 | Approach | JC-PINN test result (0.44 MPa mean curve RMSE, R² = 0.9995, 37 cases) from `reports/jc_pinn_20261107/` on branch `claude/tender-hamilton-vd2qvm` |

## Not in the project file, so the deck does not state it

The `.wbpj` holds the project structure only. Material constants, load magnitude, end time, mesh and results
are in `Comparison Study - Final_files/`, which was not supplied. So:

- **F has no magnitude.** Its direction (+Y, upper half of the bore) follows the stated load choice. The fixed support on both mounting faces matches the earlier `Elastic.wbpj`; check it against the Comparison Study set-up.
- **Slide 13 needs the three contour images and the peak stress and plastic strain values.**
- **Slide 11 says the JC-U table comes from the user's customised JC law (Equation 1).** The `.wbpj` only shows that JC-U uses a multilinear isotropic hardening table, so confirm the source.

## Rebuild

```bash
pip install gmsh==4.15.2 matplotlib numpy pillow      # gmsh needs libGLU on Linux
python presentation/build/extract_planform.py presentation/build/planform.json
python presentation/build/diagrams.py presentation/build/planform.json
NODE_PATH=<dir containing pptxgenjs> node presentation/build/build_deck.js <pptx skill dir>
```

Fonts: Calibri throughout, plus Carlito (metric-compatible with Calibri) inside the diagram images. Colours: navy `14213D`, steel `2F5D8A`, signal orange `E8590C` for loads and porosity.
