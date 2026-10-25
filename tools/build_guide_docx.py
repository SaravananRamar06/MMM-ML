import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pathlib import Path

ROOT = Path("/home/sarvn/Documents/MMM-ML")
doc = docx.Document()

# Page Margins
for s in doc.sections:
    s.top_margin = Inches(0.75)
    s.bottom_margin = Inches(0.75)
    s.left_margin = Inches(0.75)
    s.right_margin = Inches(0.75)

# Color Palette
C_PRIMARY = RGBColor(15, 23, 42)    # Slate 900
C_SECONDARY = RGBColor(30, 41, 59) # Slate 800
C_MUTED = RGBColor(71, 85, 105)    # Slate 600
C_ACCENT = RGBColor(37, 99, 235)   # Blue 600
C_CODE = RGBColor(30, 41, 59)

def set_cell_shading(cell, color_hex):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_heading_1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = C_PRIMARY
    return p

def add_heading_2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = C_SECONDARY
    return p

def add_paragraph(text, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = C_PRIMARY
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_SECONDARY
    return p

def add_bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.12
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = C_PRIMARY
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_SECONDARY
    return p

def add_code_block(code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(7.0)
    c = tbl.rows[0].cells[0]
    set_cell_shading(c, "F8FAFC")
    set_cell_margins(c, top=80, bottom=80, left=120, right=120)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(code_text)
    r.font.name = "Consolas"
    r.font.size = Pt(8.5)
    r.font.color.rgb = C_CODE

# --- HEADER ---
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(0)
p_title.paragraph_format.space_after = Pt(2)
run_title = p_title.add_run("Technical Reference & Intuitive Architecture Guide")
run_title.font.name = "Calibri"
run_title.font.size = Pt(20)
run_title.font.bold = True
run_title.font.color.rgb = C_PRIMARY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(3)
run_sub = p_sub.add_run("AlSi10Mg Flow-Stress Neural Surrogate Model: Personal Reference & Defense Guide")
run_sub.font.name = "Calibri"
run_sub.font.size = Pt(13)
run_sub.font.bold = True
run_sub.font.color.rgb = C_ACCENT

p_meta = doc.add_paragraph()
p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_meta.paragraph_format.space_after = Pt(10)
run_meta = p_meta.add_run("Material Lab Project Team • User, Gemini (Antigravity), Codex, OpenCode, Claude • October 25, 2026")
run_meta.font.name = "Calibri"
run_meta.font.size = Pt(9.5)
run_meta.font.italic = True
run_meta.font.color.rgb = C_MUTED

# Abstract Box
tbl_box = doc.add_table(rows=1, cols=1)
tbl_box.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_box.autofit = False
tbl_box.columns[0].width = Inches(7.0)
cell_box = tbl_box.rows[0].cells[0]
set_cell_shading(cell_box, "F1F5F9")
set_cell_margins(cell_box, top=100, bottom=100, left=140, right=140)

p_box = cell_box.paragraphs[0]
p_box.paragraph_format.space_after = Pt(0)
r_box_bold = p_box.add_run("Guide Purpose: ")
r_box_bold.font.bold = True
r_box_bold.font.size = Pt(9.5)
r_box_bold.font.color.rgb = C_PRIMARY
r_box_text = p_box.add_run(
    "This document serves as an accessible, end-to-end technical reference for understanding, defending, "
    "and querying the neural surrogate model developed for AlSi10Mg additive manufacturing simulations. "
    "It breaks down how neural networks, weights, and tanh activations function, traces a worked "
    "step-by-step mathematical prediction, documents the verified 5-network ensemble architecture "
    "(1,925 total parameters, 0.059085 holdout RMSE), explains the generalization spectrum, and provides "
    "plain-language answers for academic viva defense."
)
r_box_text.font.size = Pt(9.5)
r_box_text.font.color.rgb = C_SECONDARY

# 1. Motivation
add_heading_1("1. What the Model Does (In Plain English)")
add_paragraph(
    "Additive manufacturing of metallic parts (such as aerospace brackets) produces material whose stiffness and "
    "flow stress vary across different thermal and strain-rate conditions. Running a full numerical finite-element "
    "simulation for every new loading condition can take minutes or hours."
)
add_paragraph(
    "Given four environmental conditions (temperature, strain rate, density, shear modulus) and an axial strain point (E11), "
    "the surrogate model calculates the corresponding flow stress curve in 0.22 milliseconds—reproducing the simulated "
    "response with high numerical fidelity within represented conditions.",
    bold_prefix="The Surrogate Solution: "
)

add_heading_2("How Neural Networks, Weights, and Tanh Work")
add_paragraph(
    "The surrogate model is an empirical function approximator equipped with 385 adjustable parameters per network:"
)
add_bullet("Features like temperature and strain act as input signals. Because raw numerical magnitudes differ widely (e.g., G ~ 24,000 while strain ~ 0.05), we standardize them first so inputs have zero mean and unit variance.", bold_prefix="Inputs: ")
add_bullet("Each connection between layers has a numerical weight multiplier. Input influences combine nonlinearly across all layers rather than a single weight directly equaling physical sensitivity.", bold_prefix="Weights: ")
add_bullet("Each neuron has an added constant offset (bias) that sets its baseline pre-activation value.", bold_prefix="Biases: ")
add_bullet("Each neuron passes its pre-activation sum through a hyperbolic tangent (tanh) activation function, which maps values smoothly to (-1, 1). This introduces the nonlinearity required to fit smooth continuous response surfaces.", bold_prefix="Tanh Activation: ")
add_bullet("Rather than relying on a single network, we train five identical networks initialized with different random seeds. Taking their average smooths out individual fitting variations and produces a stable consensus prediction.", bold_prefix="Ensemble Averaging: ")

# 2. Worked Example
add_heading_1("2. Tracing a Step-by-Step Prediction (Worked Numerical Example)")
add_paragraph(
    "To demystify the internal math, let us trace an exact prediction using the calibrated parameters from the production runtime."
)
add_paragraph("We evaluate a material specimen under the following query inputs:")
add_bullet("Temperature (T) = 100.0 (inferred °C units)", bold_prefix="• ")
add_bullet("Strain Rate = 1e-4 (inferred s^-1 units)  -->  log10(rate) = -4.0", bold_prefix="• ")
add_bullet("Density (rho) = 2619.0 (inferred units)", bold_prefix="• ")
add_bullet("Shear Modulus (G) = 24541.0 (inferred units)", bold_prefix="• ")
add_bullet("Axial Strain (E11) = 0.049631 (grid point closest to 0.05)", bold_prefix="• ")

add_heading_2("Step A: Standardization (Z-Score)")
add_paragraph(
    "Using the training set mean and standard deviation (fitted on 4,320 training samples):"
)
add_paragraph("z = (raw_input - mean) / standard_deviation")
add_bullet("T: (100.0 - 107.22) / 68.09 = -0.1061", bold_prefix="Standardized Vector: ")
add_bullet("log10(rate): (-4.0 - (-3.92)) / 0.829 = -0.1005", bold_prefix=" ")
add_bullet("Density: (2619.0 - 2598.71) / 89.26 = +0.2273", bold_prefix=" ")
add_bullet("Shear Modulus G: (24541.0 - 24371.98) / 850.39 = +0.1988", bold_prefix=" ")
add_bullet("Strain E11: (0.049631 - 0.05005) / 0.02902 = -0.0144", bold_prefix=" ")

add_heading_2("Step B: Five-Network Ensemble Forward Evaluation")
add_paragraph(
    "The standardized vector [-0.1061, -0.1005, 0.2273, 0.1988, -0.0144] passes through the two hidden tanh layers "
    "of each network. The standardized outputs produced by the five committee networks are:"
)
add_bullet("Network 0 (Seed 0):  z0 = +0.068864", bold_prefix="Individual Network Outputs: ")
add_bullet("Network 1 (Seed 1):  z1 = +0.071352", bold_prefix=" ")
add_bullet("Network 2 (Seed 2):  z2 = +0.066148", bold_prefix=" ")
add_bullet("Network 3 (Seed 3):  z3 = +0.066717", bold_prefix=" ")
add_bullet("Network 4 (Seed 4):  z4 = +0.067810", bold_prefix=" ")

add_heading_2("Step C: Ensemble Averaging & Unscaling")
add_paragraph(
    "1. Average Standardized Output:  z_avg = (0.068864 + 0.071352 + 0.066148 + 0.066717 + 0.067810) / 5 = +0.068178\n"
    "2. Inverse Scaling to Inferred Stress Units (training target mean = 97.7665, target std = 27.3756):\n"
    "   Predicted Stress = z_avg * target_std + target_mean\n"
    "   Predicted Stress = 0.068178 * 27.3756 + 97.7665 = 99.6329 (inferred stress units)\n"
    "3. Exact Interpolation to E11 = 0.05000 yields: 99.4186 (inferred stress units)."
)

# 3. Training vs Inference
add_heading_1("3. Training vs. Inference, L-BFGS & Regularization")
add_paragraph(
    "It is essential to distinguish between the two distinct lifecycle phases of the model:"
)
add_bullet("The fitting phase where the algorithm determines the 385 numerical weights per network. Using the L-BFGS optimizer on the 4,320 training grid points, training completes in 25.0 seconds for all 5 networks.", bold_prefix="Training Phase: ")
add_bullet("The operational deployment phase. The weights are frozen into an 18 KB NPZ file. Calculating a full 120-point curve requires only matrix multiplications and tanh evaluations, taking 0.221 milliseconds.", bold_prefix="Inference Phase: ")

add_heading_2("L-BFGS and L2 Regularization (alpha = 0.001)")
add_bullet("For moderately sized tabular datasets (4,320 samples), L-BFGS (a quasi-Newton 2nd-order method) uses gradient history to approximate the Hessian curvature, efficiently converging to a local minimum on the empirical loss surface without convergence warnings.", bold_prefix="L-BFGS Optimizer: ")
add_bullet("L2 weight regularization (penalty alpha = 0.001) penalizes large weight magnitudes, discouraging rapid oscillation between query coordinates.", bold_prefix="L2 Regularization (alpha = 0.001): ")

# 4. Dataset & Splitting
add_heading_1("4. Dataset Provenance & Case-Level Splitting")
add_paragraph(
    "The simulation dataset contains 73 complete flow-stress histories. The underlying finite element files contain "
    "2,197,000 raw rows (1,224,000 in the training cases, 973,000 in the holdout cases). These raw rows represent output time-steps, "
    "not independent data samples. Each simulation curve is interpolated onto a standardized 120-point axial strain grid."
)
add_bullet("Fitting operates on 4,320 query samples (36 cases x 120 strain points).", bold_prefix="Training Queries: ")
add_bullet("Evaluation operates on 4,440 query samples (37 cases x 120 strain points).", bold_prefix="Holdout Queries: ")

add_heading_2("Why We Split by Case, Not by Row")
add_paragraph(
    "If data were partitioned randomly by row, neighboring strain coordinates from the same simulation curve would appear "
    "in both partitions, yielding heavily overoptimistic evaluation scores. By partitioning strictly by simulation ID, "
    "the holdout set evaluates how well the model predicts entirely separate simulation histories.",
    bold_prefix="Avoiding Correlated Point Leakage: "
)
add_paragraph(
    "The split was established using a reproducible pseudo-random seed on simulation IDs (36 train, 37 test). "
    "Standardizers were fitted strictly on the 4,320 training grid queries. Earlier all-data exploration and feature selection "
    "were conducted on the dataset. The final split is a disjoint case partition rather than an untouched blind benchmark.",
    bold_prefix="Prior Exploration Disclosure: "
)

add_heading_2("Compact Operational Input Range Table")
add_paragraph("Summary of valid operational ranges inside the training domain. Note: Units are inferred and generalization on unseen condition combinations is not guaranteed:")

tbl_range = doc.add_table(rows=1, cols=5)
tbl_range.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_range.autofit = False
r_widths = [Inches(1.5), Inches(1.2), Inches(1.2), Inches(1.1), Inches(2.0)]

r_hdr_cells = tbl_range.rows[0].cells
r_hdr_titles = ["Feature", "Physical Range", "Internal Encoding", "Inferred Unit", "Operational Guidance"]
for idx, title in enumerate(r_hdr_titles):
    r_hdr_cells[idx].width = r_widths[idx]
    set_cell_shading(r_hdr_cells[idx], "E2E8F0")
    set_cell_margins(r_hdr_cells[idx], top=60, bottom=60, left=80, right=80)
    p = r_hdr_cells[idx].paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(title)
    r.font.bold = True
    r.font.size = Pt(8.5)
    r.font.color.rgb = C_PRIMARY

range_data = [
    ("Temperature (T)", "30.0 .. 200.0", "30.0 .. 200.0", "°C (inferred)", "Strictly [30, 200]; 300 °C extrapolation invalid"),
    ("Strain Rate", "1e-5 .. 1e-3", "-5.0 .. -3.0", "s^-1 (inferred)", "Always log10-transformed before network input"),
    ("Density (rho)", "2488.05 .. 2700.0", "2488.05 .. 2700.0", "kg/m³ (inferred)", "Minor sensitivity (~0.19 units); no porosity link"),
    ("Shear Modulus (G)", "23313.95 .. 25300.0", "23313.95 .. 25300.0", "MPa (inferred)", "Numeric stiffness input; no porosity proxy"),
    ("Axial Strain (E11)", "0.0002 .. 0.0999", "0.0002 .. 0.0999", "Strain", "Standardized 120-point monotonic loading grid")
]

for row in range_data:
    r_cells = tbl_range.add_row().cells
    for idx, val in enumerate(row):
        r_cells[idx].width = r_widths[idx]
        set_cell_margins(r_cells[idx], top=40, bottom=40, left=80, right=80)
        p = r_cells[idx].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.size = Pt(8)
        if idx == 0:
            r.font.bold = True
            r.font.color.rgb = C_PRIMARY
        else:
            r.font.color.rgb = C_SECONDARY

doc.add_paragraph().paragraph_format.space_after = Pt(4)

# 5. Verification & Generalization
add_heading_1("5. Three-Tier Verification & The Generalization Spectrum")
add_paragraph("The model was subjected to a rigorous 3-tier audit:")
add_bullet("The 120-point interpolated grid for all 73 curves was audited against raw STR_STR.OUT files and SHA256 hashes. Maximum absolute difference = 0.0.", bold_prefix="Tier 1 (Cache Verification): ")
add_bullet("Evaluating the frozen ensemble on the 37 holdout cases reproduced the exact saved metrics: Mean Test RMSE = 0.05908515 (worst case: 0.11330618, Case 45).", bold_prefix="Tier 2 (Holdout Artifact Reload): ")
add_bullet("A completely independent refit of all five seeds on the 36 training cases took 25.0 seconds, producing zero warnings and reproducing all weights and predictions with 0.0 max absolute difference.", bold_prefix="Tier 3 (Same-Environment Reproduction): ")

# Table
tbl_metrics = doc.add_table(rows=1, cols=4)
tbl_metrics.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_metrics.autofit = False
widths = [Inches(2.4), Inches(1.1), Inches(1.3), Inches(2.2)]

hdr_cells = tbl_metrics.rows[0].cells
hdr_titles = ["Evaluation Regime", "Metric", "Value (Stress Units)", "Context / Interpretation"]
for idx, title in enumerate(hdr_titles):
    hdr_cells[idx].width = widths[idx]
    set_cell_shading(hdr_cells[idx], "E2E8F0")
    set_cell_margins(hdr_cells[idx], top=70, bottom=70, left=90, right=90)
    p = hdr_cells[idx].paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(title)
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = C_PRIMARY

rows_data = [
    ("Holdout Test Set (37 cases)", "Mean RMSE", "0.059085", "Within-condition interpolation fidelity"),
    ("Holdout Test Set", "Worst RMSE", "0.113306", "Case 45 (T=100, rate=1e-4)"),
    ("Training Case CV (36 cases)", "Mean RMSE", "1.158263", "Cross-case variability across folds"),
    ("Training Case CV", "Median RMSE", "0.201877", "Half of training cases have RMSE <= 0.201877"),
    ("Leave-Condition-Out (LOCO)", "Mean of Conds", "6.793603", "Average generalization to unseen conditions"),
    ("Leave-Condition-Out (Hot/Slow)", "Condition Mean", "23.525129", "200 °C, 1e-5 s^-1 extreme corner")
]

for row in rows_data:
    r_cells = tbl_metrics.add_row().cells
    for idx, val in enumerate(row):
        r_cells[idx].width = widths[idx]
        set_cell_margins(r_cells[idx], top=50, bottom=50, left=90, right=90)
        p = r_cells[idx].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.size = Pt(8.5)
        if idx == 2:
            r.font.bold = True
            r.font.color.rgb = C_ACCENT
        else:
            r.font.color.rgb = C_SECONDARY

doc.add_paragraph().paragraph_format.space_after = Pt(3)

add_heading_2("Understanding the Generalization Spectrum: Interpolation vs. Extrapolation")
add_paragraph(
    "Root Mean Squared Error measures average prediction error along curve points. Why is Test RMSE 0.059 while Leave-Condition-Out RMSE is 6.79?"
)
add_bullet("All 8 temperature and strain-rate combinations in the test set exist in the training set. The model is interpolating along smooth curves for known conditions, yielding near-zero error (0.059).", bold_prefix="Within-Condition Interpolation (0.059 RMSE): ")
add_bullet("When an entire operating condition is held out, the model must predict without anchor curves. Held-out interior levels (e.g., 100 °C, 1e-4 s^-1) represent interpolation to unseen conditions (RMSE ~5.2). Boundary corners (e.g., 200 °C, 1e-5 s^-1) represent extrapolation across extreme edges, where condition mean error reaches 23.53.", bold_prefix="Unseen Condition Generalization (6.79 - 23.53 RMSE): ")

add_paragraph(
    "In training cross-validation, Case 60 exhibits high error (RMSE = 25.99). Its recorded von Mises strain reverses "
    "while axial strain E11 increases. The generating cause of this behavior is unknown. It is retained and flagged as "
    "genuine evidence of limited generalization under irregular yield behavior.",
    bold_prefix="The Case 60 Anomaly: "
)

# 6. Runtime Benchmarks
add_heading_1("6. Runtime Performance & Benchmarks")
add_paragraph("An optimized NumPy-only runtime was developed (src/query_runtime.py) to eliminate the heavy scikit-learn dependency:")
add_bullet("Stored in an 18,462-byte pickle-free .npz file (vs 62,940 bytes Joblib bundle).", bold_prefix="Weight Storage: ")
add_bullet("0.221 ms (NumPy) vs 0.511 ms (scikit-learn) for full 120-point curve prediction in local repeated single-thread benchmarks.", bold_prefix="Full-Curve Latency: ")
add_bullet("163 ms (NumPy) vs 976 ms (scikit-learn).", bold_prefix="Cold Startup Time: ")
add_bullet("On full-batch evaluation (73 cases), scikit-learn took 17.3 ms vs NumPy 21.8 ms under identical single-thread BLAS settings.", bold_prefix="Full-Batch Caveat: ")
add_bullet("Exactly 0.0 max absolute difference against reference model outputs across all 73 curves.", bold_prefix="Accuracy Parity: ")

# 7. Executable Code
add_heading_1("7. Verified Executable Code Example")
add_paragraph("The following code loads the lightweight NumPy runtime, runs inference on a test case, and queries a point:")

code_example = (
    "import numpy as np\n"
    "from src.query_runtime import QueryRuntime\n\n"
    "# 1. Load lightweight runtime (18 KB pickle-free NPZ)\n"
    "runtime = QueryRuntime.load('runs/score/final_Svm/model_numpy.npz')\n\n"
    "# 2. Define input case: [T, log10(strain_rate), density, shear_modulus]\n"
    "X_case = np.array([[100.0, -4.0, 2619.0, 24541.0]])\n\n"
    "# 3. Predict full 120-point flow-stress curve\n"
    "curve = runtime.predict(X_case)[0]\n"
    "print(f'Curve shape: {curve.shape}')  # (120,)\n\n"
    "# 4. Query stress at a specific strain point (e.g., E11 = 0.05)\n"
    "stress_at_point = np.interp(0.05, runtime.strain, curve)\n"
    "print(f'Flow Stress at E11=0.05: {stress_at_point:.4f} (inferred units)')\n"
)
add_code_block(code_example)

# 8. Reproducibility
add_heading_1("8. Exact Reproducible Commands & Evidence Paths")
add_paragraph("All findings and metrics in this report can be independently audited using the following commands:")
add_code_block(
    "# 1. Audit raw simulation rows, cache integrity, and saved model reload:\n"
    ".venv/bin/python reports/verify_final_model.py\n\n"
    "# 2. Reproduce fresh training across all 5 seeds from scratch (25.0s):\n"
    ".venv/bin/python reports/reproduce_final_training.py\n\n"
    "# 3. Run test suite (13 model, parser, and runtime tests):\n"
    ".venv/bin/python -m unittest discover -s tests -p \"test_*.py\" -v\n\n"
    "# 4. Run single-curve and batch runtime benchmarks:\n"
    ".venv/bin/python reports/benchmark_query_runtime.py\n"
)

add_paragraph("Key evidence JSON files:", bold_prefix="Artifact Provenance: ")
add_bullet("reports/model_verification_20261025.json (Audit results and metrics)", bold_prefix="• ")
add_bullet("reports/final_training_reproduction_20261025.json (Refit timing and weight parity)", bold_prefix="• ")
add_bullet("reports/query_runtime_benchmark_20261025.json (Latency and file size measurements)", bold_prefix="• ")

# 9. Viva Q&A
add_heading_1("9. Operational Boundaries & Viva Defense Q&A Guide")

qa_items = [
    ("Q1: What are the units of your predicted stress?",
     "The raw simulation files report stress without explicit unit headers. The model predictions are evaluated in "
     "inferred stress units (RMSE = 0.059). While numerically consistent across all profiles, we explicitly treat them "
     "as inferred stress units rather than confirmed MPa until the simulator's exact constitutive definitions are verified."),
    ("Q2: Does your model predict true plastic strain?",
     "No. The input variable is E11, which is the operational axial strain coordinate reported by the simulation output, "
     "not verified true plastic strain."),
    ("Q3: Can your model predict flow stress at 300 °C?",
     "No. The training data strictly spans 30 °C to 200 °C. Unconstrained MLPs predict unphysical negative stress when "
     "extrapolated to 300 °C. Operational use must strictly remain within [30 °C, 200 °C]."),
    ("Q4: Can this model predict wing-rib bracket aerodynamic lift (C_L)?",
     "No. This is a material-level flow-stress surrogate along the supplied uniaxial loading family. The simulation matrix "
     "models constitutive stress-strain histories, not aerodynamic coefficients. No bracket structural FEA integration has been validated."),
    ("Q5: Can you claim zero data leakage?",
     "We claim a strictly disjoint case partition for final fitting and evaluation. However, earlier all-data exploration "
     "and feature selection were conducted on the dataset. We maintain scientific honesty by reporting this exploration "
     "rather than claiming an untouched blind holdout.")
]

for q, a in qa_items:
    add_paragraph(q, bold_prefix="")
    add_paragraph(a, bold_prefix="Answer: ")

output_docx = ROOT / "reports/model_guide.docx"
doc.save(output_docx)
print("Saved DOCX successfully:", output_docx)
