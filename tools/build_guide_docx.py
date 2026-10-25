#!/usr/bin/env python3
"""Executive Document Generator: AlSi10Mg Neural Surrogate Flow-Stress Model Reference Guide
Generates professionally styled, publication-grade .docx, .doc, and .pdf documents with WCAG contrast,
custom table borders, executive callouts, and exact verified mathematical predictions.
"""

import os
import subprocess
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

ROOT = Path("/home/sarvn/Documents/MMM-ML")
PROJECT_FILES = ROOT / "project files"
REPORTS_DIR = ROOT / "reports"

doc = docx.Document()

# Page Margins: 0.75 inch for balanced, compact pagination
for s in doc.sections:
    s.top_margin = Inches(0.75)
    s.bottom_margin = Inches(0.75)
    s.left_margin = Inches(0.75)
    s.right_margin = Inches(0.75)

# Color Palette: Executive Slate & Royal Accent
C_NAVY = RGBColor(15, 23, 42)       # Slate 900 (Headings, primary emphasis)
C_SLATE = RGBColor(51, 65, 85)      # Slate 700 (Body text - crisp & readable)
C_MUTED = RGBColor(100, 116, 139)   # Slate 500 (Captions, footnotes, metadata)
C_BLUE = RGBColor(37, 99, 235)      # Blue 600 (Primary accent, highlights)
C_CODE = RGBColor(226, 232, 240)    # Light slate for dark code block text

# ----------------- XML Helpers -----------------

def set_cell_shading(cell, color_hex):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def make_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def make_header_repeat(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def add_callout_box(text_paragraphs, bg_hex="F8FAFC", border_hex="2563EB", border_sz="24"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.9)
    make_row_cant_split(tbl.rows[0])

    c = tbl.rows[0].cells[0]
    set_cell_shading(c, bg_hex)
    set_cell_margins(c, top=120, bottom=120, left=160, right=140)

    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_hex}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    c._tc.get_or_add_tcPr().append(borders)

    for idx, (p_text, bold_prefix, is_bold) in enumerate(text_paragraphs):
        p = c.paragraphs[0] if idx == 0 else c.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.name = "Calibri"
            r_bold.font.size = Pt(10)
            r_bold.font.bold = True
            r_bold.font.color.rgb = C_NAVY
        if p_text:
            r_text = p.add_run(p_text)
            r_text.font.name = "Calibri"
            r_text.font.size = Pt(10)
            r_text.font.bold = is_bold
            r_text.font.color.rgb = C_SLATE

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(2)

def add_heading_1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = C_NAVY
    return p

def add_heading_2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = C_BLUE
    return p

def add_paragraph(text, bold_prefix=None, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.18
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = C_NAVY
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.color.rgb = C_SLATE
    return p

def add_bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = C_NAVY
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.color.rgb = C_SLATE
    return p

def add_code_block(code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.9)
    make_row_cant_split(tbl.rows[0])

    c = tbl.rows[0].cells[0]
    set_cell_shading(c, "0F172A")
    set_cell_margins(c, top=80, bottom=80, left=120, right=120)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(code_text)
    r.font.name = "Consolas"
    r.font.size = Pt(8.5)
    r.font.color.rgb = C_CODE
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(2)

# ----------------- DOCUMENT HEADER -----------------

p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(6)
p_title.paragraph_format.space_after = Pt(2)
run_title = p_title.add_run("Technical Reference & Intuitive Architecture Guide")
run_title.font.name = "Calibri"
run_title.font.size = Pt(20)
run_title.font.bold = True
run_title.font.color.rgb = C_NAVY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(2)
run_sub = p_sub.add_run("AlSi10Mg Flow-Stress Neural Surrogate Model: Personal Reference & Defense Guide")
run_sub.font.name = "Calibri"
run_sub.font.size = Pt(12)
run_sub.font.bold = True
run_sub.font.color.rgb = C_BLUE

p_meta = doc.add_paragraph()
p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_meta.paragraph_format.space_after = Pt(10)
run_meta = p_meta.add_run("Material Lab Project Team • User, Gemini, Codex, OpenCode, Claude • October 25, 2026")
run_meta.font.name = "Calibri"
run_meta.font.size = Pt(9.5)
run_meta.font.italic = True
run_meta.font.color.rgb = C_MUTED

# Executive Summary Callout Box
add_callout_box([
    ("This document serves as an accessible, end-to-end technical reference for understanding, defending, "
     "and querying the neural surrogate model developed for AlSi10Mg additive manufacturing simulations. "
     "It breaks down how neural networks, weights, biases, and tanh activations function intuitively, traces an exact "
     "numerical prediction step-by-step, documents the verified 5-network ensemble architecture "
     "(1,925 total parameters, 0.059085 holdout RMSE), explains the generalization spectrum, and provides "
     "plain-language answers for academic viva defense.",
     "Guide Purpose & Overview: ", False)
], bg_hex="F1F5F9", border_hex="2563EB")

# ----------------- 1. WHAT THE MODEL DOES -----------------
add_heading_1("1. What the Model Does (In Plain English)")

add_paragraph(
    "Additive manufacturing of metallic parts (such as aerospace brackets) produces material whose stiffness and "
    "flow stress vary across different thermal and strain-rate conditions. Full numerical finite-element simulations "
    "often require significant computation time; the neural surrogate provides rapid local evaluation within represented training conditions."
)

add_paragraph(
    "Given four environmental conditions (temperature, strain rate, density, shear modulus) and an axial strain point (E11), "
    "the surrogate model evaluates the corresponding flow stress curve in 0.221 ms (local measured NumPy warm single-curve median latency "
    "across 120 points on single-thread BLAS)—reproducing the simulated response with high numerical fidelity within represented conditions.",
    bold_prefix="The Surrogate Solution: "
)

add_heading_2("How Neural Networks, Weights, and Tanh Work")
add_paragraph("The surrogate model is an empirical function approximator equipped with 385 adjustable parameters per network (weights plus biases):")
add_bullet("Features like temperature and strain act as input signals. Because raw numerical magnitudes differ widely (e.g., G ~ 24,000 while strain ~ 0.05), we standardize them first so inputs have zero mean and unit variance.", bold_prefix="Inputs: ")
add_bullet("Each connection between layers has a numerical weight multiplier. Input influences combine nonlinearly across all layers rather than a single weight directly equaling physical sensitivity.", bold_prefix="Weights & Biases: ")
add_bullet("Each neuron passes its pre-activation sum through a hyperbolic tangent (tanh) activation function, which maps values smoothly to (-1, 1). This introduces the nonlinearity required to fit smooth continuous response surfaces.", bold_prefix="Tanh Activation: ")
add_bullet("Rather than relying on a single network, we train five identical networks initialized with different random seeds. Taking their average smooths out individual fitting variations and produces a stable consensus prediction.", bold_prefix="Ensemble Averaging: ")

# ----------------- 2. WORKED NUMERICAL PREDICTION -----------------
add_heading_1("2. Tracing a Step-by-Step Prediction (Worked Numerical Example)")

add_paragraph("To demystify the internal math, let us trace an exact prediction using the calibrated parameters from the production runtime.")
add_paragraph("We evaluate a material specimen under the following query inputs:")
add_bullet("100.0 (inferred °C units)", bold_prefix="Temperature (T): ")
add_bullet("1e-4 (inferred s^-1 units)  -->  log10(rate) = -4.0", bold_prefix="Strain Rate: ")
add_bullet("2619.0 (inferred units)", bold_prefix="Density (rho): ")
add_bullet("24541.0 (inferred units)", bold_prefix="Shear Modulus (G): ")
add_bullet("0.049631 (standardized grid point closest to 0.05)", bold_prefix="Axial Strain (E11): ")

add_heading_2("Step A: Input Standardization (Z-Score)")
add_paragraph("Using the training set mean and standard deviation fitted on the 4,320 training samples, every feature is standardized via z = (x - μ) / σ:")

# Step A Table
tbl_step_a = doc.add_table(rows=1, cols=5)
tbl_step_a.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_step_a.autofit = False
set_table_borders(tbl_step_a)
w_a = [Inches(1.8), Inches(1.2), Inches(1.3), Inches(1.2), Inches(1.4)]

headers_a = ["Feature", "Raw Input (x)", "Mean (μ)", "Std Dev (σ)", "Standardized (z)"]
make_header_repeat(tbl_step_a.rows[0])
make_row_cant_split(tbl_step_a.rows[0])

for idx, h in enumerate(headers_a):
    c = tbl_step_a.rows[0].cells[idx]
    c.width = w_a[idx]
    set_cell_shading(c, "1E293B")
    set_cell_margins(c, top=80, bottom=80, left=100, right=100)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(h)
    r.font.name = "Calibri"
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(255, 255, 255)

data_a = [
    ("Temperature (T)", "100.0", "107.22", "68.09", "-0.1061"),
    ("Strain Rate log10(rate)", "-4.0", "-3.92", "0.829", "-0.1005"),
    ("Density (rho)", "2619.0", "2598.71", "89.26", "+0.2273"),
    ("Shear Modulus (G)", "24541.0", "24371.98", "850.39", "+0.1988"),
    ("Axial Strain (E11)", "0.049631", "0.05005", "0.02902", "-0.0144")
]

for row_idx, row in enumerate(data_a):
    r_cells = tbl_step_a.add_row().cells
    make_row_cant_split(tbl_step_a.rows[row_idx + 1])
    shading = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
    for idx, val in enumerate(row):
        r_cells[idx].width = w_a[idx]
        set_cell_shading(r_cells[idx], shading)
        set_cell_margins(r_cells[idx], top=60, bottom=60, left=100, right=100)
        p = r_cells[idx].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(val)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        if idx == 4:
            r.font.bold = True
            r.font.color.rgb = C_BLUE
        else:
            r.font.color.rgb = C_SLATE

doc.add_paragraph().paragraph_format.space_after = Pt(2)

add_heading_2("Step B: Five-Network Ensemble Forward Evaluation")
add_paragraph("The standardized input vector [-0.1061, -0.1005, +0.2273, +0.1988, -0.0144] passes through the 2 hidden tanh layers (16 neurons each) of all 5 committee networks:")

# Step B Table - Keep together with cantSplit
tbl_step_b = doc.add_table(rows=1, cols=3)
tbl_step_b.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_step_b.autofit = False
set_table_borders(tbl_step_b)
w_b = [Inches(2.5), Inches(2.0), Inches(2.4)]
make_header_repeat(tbl_step_b.rows[0])
make_row_cant_split(tbl_step_b.rows[0])

headers_b = ["Network Instance", "Random Seed", "Standardized Output (z_i)"]
for idx, h in enumerate(headers_b):
    c = tbl_step_b.rows[0].cells[idx]
    c.width = w_b[idx]
    set_cell_shading(c, "1E293B")
    set_cell_margins(c, top=80, bottom=80, left=100, right=100)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if idx == 2 else WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(h)
    r.font.name = "Calibri"
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(255, 255, 255)

data_b = [
    ("Network 0", "Seed 0", "+0.068864"),
    ("Network 1", "Seed 1", "+0.071352"),
    ("Network 2", "Seed 2", "+0.066148"),
    ("Network 3", "Seed 3", "+0.066717"),
    ("Network 4", "Seed 4", "+0.067810")
]

for row_idx, row in enumerate(data_b):
    r_cells = tbl_step_b.add_row().cells
    make_row_cant_split(tbl_step_b.rows[row_idx + 1])
    shading = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
    for idx, val in enumerate(row):
        r_cells[idx].width = w_b[idx]
        set_cell_shading(r_cells[idx], shading)
        set_cell_margins(r_cells[idx], top=60, bottom=60, left=100, right=100)
        p = r_cells[idx].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if idx == 2 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(val)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        if idx == 2:
            r.font.bold = True
            r.font.color.rgb = C_BLUE
        else:
            r.font.color.rgb = C_SLATE

doc.add_paragraph().paragraph_format.space_after = Pt(2)

add_heading_2("Step C: Committee Averaging & Inverse Scaling")

add_callout_box([
    ("z_avg = (0.068864 + 0.071352 + 0.066148 + 0.066717 + 0.067810) / 5 = +0.068178",
     "1. Ensemble Average Output: ", False),
    ("Predicted Stress = z_avg * target_std + target_mean\n"
     "Predicted Stress = 0.068178 * 27.3756 + 97.7665 = 99.6329 (inferred stress units)",
     "2. Inverse Scaling (target mean μ = 97.7665, target std σ = 27.3756): ", False),
    ("Evaluating along the full 120-point strain profile and interpolating directly to E11 = 0.05000:\n"
     "Flow Stress at E11 = 0.05000 is 99.4186 (inferred stress units).",
     "3. Exact Target Grid Point (E11 = 0.05000): ", True)
], bg_hex="F8FAFC", border_hex="3B82F6")

# ----------------- 3. TRAINING VS INFERENCE -----------------
add_heading_1("3. Training vs. Inference, L-BFGS & Regularization")

add_paragraph("It is essential to distinguish between the two distinct lifecycle phases of the surrogate:")
add_bullet("The fitting phase where the algorithm optimizes the 385 numerical parameters (weights and biases) per network. Using the quasi-Newton L-BFGS optimizer on the 4,320 training grid points, training completes in 25.0 seconds for all 5 networks with zero warnings.", bold_prefix="Training Phase: ")
add_bullet("The operational deployment phase. The parameters are frozen into an 18 KB NPZ file. Calculating a full 120-point curve requires only matrix multiplications and tanh evaluations, taking 0.221 ms local measured median.", bold_prefix="Inference Phase: ")

add_heading_2("L-BFGS and L2 Regularization (alpha = 0.001)")
add_bullet("For moderately sized tabular datasets (4,320 samples), L-BFGS uses gradient history to approximate the Hessian curvature, efficiently converging to a local minimum on the empirical loss surface without convergence warnings.", bold_prefix="L-BFGS Optimizer: ")
add_bullet("L2 parameter regularization (penalty alpha = 0.001) penalizes large weight magnitudes, discouraging rapid oscillation between query coordinates.", bold_prefix="L2 Regularization: ")

# ----------------- 4. DATASET & SPLITTING -----------------
add_heading_1("4. Dataset Provenance & Case-Level Splitting")

add_paragraph(
    "The simulation dataset contains 73 complete flow-stress histories. The underlying finite element files contain "
    "2,197,000 raw rows (1,224,000 in the training cases, 973,000 in the holdout cases). These raw rows represent output time-steps, "
    "not independent data samples. Each simulation curve is interpolated onto a standardized 120-point axial strain grid."
)
add_bullet("4,320 query samples (36 cases x 120 strain points).", bold_prefix="Training Queries: ")
add_bullet("4,440 query samples (37 cases x 120 strain points).", bold_prefix="Holdout Queries: ")

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
add_paragraph("Summary of valid operational ranges inside the training domain. Note: All units are inferred and generalization on unseen condition combinations is not guaranteed:")

# Input Range Table
tbl_range = doc.add_table(rows=1, cols=5)
tbl_range.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_range.autofit = False
set_table_borders(tbl_range)
w_r = [Inches(1.5), Inches(1.2), Inches(1.2), Inches(1.1), Inches(1.9)]
make_header_repeat(tbl_range.rows[0])
make_row_cant_split(tbl_range.rows[0])

r_headers = ["Feature", "Physical Range", "Internal Encoding", "Inferred Unit", "Operational Guidance"]
for idx, h in enumerate(r_headers):
    c = tbl_range.rows[0].cells[idx]
    c.width = w_r[idx]
    set_cell_shading(c, "1E293B")
    set_cell_margins(c, top=80, bottom=80, left=80, right=80)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = "Calibri"
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(255, 255, 255)

range_data = [
    ("Temperature (T)", "30.0 .. 200.0", "30.0 .. 200.0", "°C (inferred)", "Strictly [30, 200]; 300 °C extrapolation invalid"),
    ("Strain Rate", "1e-5 .. 1e-3", "-5.0 .. -3.0", "s^-1 (inferred)", "Always log10-transformed before network input"),
    ("Density (rho)", "2488.05 .. 2700.0", "2488.05 .. 2700.0", "kg/m³ (inferred)", "Minor sensitivity (~0.19 units); no porosity link"),
    ("Shear Modulus (G)", "23313.95 .. 25300.0", "23313.95 .. 25300.0", "MPa (inferred)", "Numeric stiffness input; no porosity proxy"),
    ("Axial Strain (E11)", "0.0002 .. 0.0999", "0.0002 .. 0.0999", "Strain", "Standardized 120-point monotonic loading grid")
]

for row_idx, row in enumerate(range_data):
    r_cells = tbl_range.add_row().cells
    make_row_cant_split(tbl_range.rows[row_idx + 1])
    shd = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
    for idx, val in enumerate(row):
        r_cells[idx].width = w_r[idx]
        set_cell_shading(r_cells[idx], shd)
        set_cell_margins(r_cells[idx], top=60, bottom=60, left=80, right=80)
        p = r_cells[idx].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        if idx == 0:
            r.font.bold = True
            r.font.color.rgb = C_NAVY
        else:
            r.font.color.rgb = C_SLATE

doc.add_paragraph().paragraph_format.space_after = Pt(2)

# ----------------- 5. VERIFICATION & GENERALIZATION -----------------
add_heading_1("5. Three-Tier Verification & The Generalization Spectrum")

add_paragraph("The model was subjected to a rigorous 3-tier audit:")
add_bullet("The 120-point interpolated grid for all 73 curves was audited against raw STR_STR.OUT files and SHA256 hashes. Maximum absolute difference = 0.0.", bold_prefix="Tier 1 (Cache Verification): ")
add_bullet("Evaluating the frozen ensemble on the 37 holdout cases reproduced the exact saved metrics: Mean Test RMSE = 0.05908515 (worst case: 0.11330618, Case 45).", bold_prefix="Tier 2 (Holdout Artifact Reload): ")
add_bullet("A completely independent refit of all five seeds on the 36 training cases took 25.0 seconds, producing zero warnings and reproducing all weights and predictions with 0.0 max absolute difference.", bold_prefix="Tier 3 (Same-Environment Reproduction): ")

# Verification Table
tbl_metrics = doc.add_table(rows=1, cols=4)
tbl_metrics.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_metrics.autofit = False
set_table_borders(tbl_metrics)
w_m = [Inches(2.4), Inches(1.2), Inches(1.3), Inches(2.0)]
make_header_repeat(tbl_metrics.rows[0])
make_row_cant_split(tbl_metrics.rows[0])

m_headers = ["Evaluation Regime", "Metric", "Value (Stress Units)", "Context / Interpretation"]
for idx, h in enumerate(m_headers):
    c = tbl_metrics.rows[0].cells[idx]
    c.width = w_m[idx]
    set_cell_shading(c, "1E293B")
    set_cell_margins(c, top=80, bottom=80, left=80, right=80)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = "Calibri"
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(255, 255, 255)

rows_data = [
    ("Holdout Test Set (37 cases)", "Mean RMSE", "0.059085", "Within-condition interpolation fidelity"),
    ("Holdout Test Set", "Worst RMSE", "0.113306", "Case 45 (T=100, rate=1e-4)"),
    ("Training Case CV (36 cases)", "Mean RMSE", "1.158263", "Cross-case variability across folds"),
    ("Training Case CV", "Median RMSE", "0.201877", "Half of training cases have RMSE <= 0.201877"),
    ("Leave-Condition-Out (LOCO)", "Mean of Conds", "6.793603", "Average generalization to unseen conditions"),
    ("Leave-Condition-Out (Hot/Slow)", "Condition Mean", "23.525129", "200 °C, 1e-5 s^-1 extreme corner")
]

for row_idx, row in enumerate(rows_data):
    r_cells = tbl_metrics.add_row().cells
    make_row_cant_split(tbl_metrics.rows[row_idx + 1])
    shd = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
    for idx, val in enumerate(row):
        r_cells[idx].width = w_m[idx]
        set_cell_shading(r_cells[idx], shd)
        set_cell_margins(r_cells[idx], top=60, bottom=60, left=80, right=80)
        p = r_cells[idx].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        if idx == 2:
            r.font.bold = True
            r.font.color.rgb = C_BLUE
        else:
            r.font.color.rgb = C_SLATE

doc.add_paragraph().paragraph_format.space_after = Pt(2)

add_heading_2("Understanding the Generalization Spectrum: Interpolation vs. Extrapolation")
add_paragraph("Root Mean Squared Error measures average prediction error along curve points. Why is Test RMSE 0.059 while Leave-Condition-Out RMSE is 6.79?")
add_bullet("All 8 temperature and strain-rate combinations in the test set exist in the training set. The model is interpolating along smooth curves for known conditions, yielding near-zero error (0.059).", bold_prefix="Within-Condition Interpolation (0.059 RMSE): ")
add_bullet("When an entire operating condition is held out, the model must predict without anchor curves. Held-out interior levels (e.g., 100 °C, 1e-4 s^-1) represent interpolation to unseen conditions (RMSE ~5.2). Boundary corners (e.g., 200 °C, 1e-5 s^-1) represent extrapolation across extreme edges, where condition mean error reaches 23.53.", bold_prefix="Unseen Condition Generalization (6.79 - 23.53 RMSE): ")

add_paragraph(
    "In training cross-validation, Case 60 exhibits an observed reversal in von Mises strain while axial strain E11 increases. "
    "The underlying cause of this recorded profile in the simulation output is unknown; it is retained as an observed outlier in the training CV record.",
    bold_prefix="The Case 60 Observation: "
)

# ----------------- 6. RUNTIME BENCHMARKS -----------------
add_heading_1("6. Runtime Performance & Benchmarks")
add_paragraph("An optimized NumPy-only runtime was developed (src/query_runtime.py) to eliminate the heavy scikit-learn dependency:")
add_bullet("Stored in an 18,462-byte pickle-free .npz file (vs 62,940 bytes Joblib bundle).", bold_prefix="Weight Storage: ")
add_bullet("0.221 ms (NumPy) vs 0.511 ms (scikit-learn) for full 120-point curve prediction in local repeated single-thread benchmarks.", bold_prefix="Full-Curve Latency: ")
add_bullet("163 ms (NumPy) vs 976 ms (scikit-learn).", bold_prefix="Cold Startup Time: ")
add_bullet("On full-batch evaluation (73 cases), scikit-learn took 17.3 ms vs NumPy 21.8 ms under identical single-thread BLAS settings.", bold_prefix="Full-Batch Caveat: ")
add_bullet("Exactly 0.0 max absolute difference against reference model outputs across all 73 curves.", bold_prefix="Accuracy Parity: ")

# ----------------- 7. EXECUTABLE CODE -----------------
add_heading_1("7. Verified Executable Code Example")
p_intro = add_paragraph("The following code loads the lightweight NumPy runtime, runs inference on a test case, and queries a point:")
p_intro.paragraph_format.keep_with_next = True

code_example = (
    "import numpy as np\n"
    "from src.query_runtime import QueryRuntime\n\n"
    "# 1. Load lightweight runtime (18 KB pickle-free NPZ)\n"
    "runtime = QueryRuntime.load('runs/score/final_Svm/model_numpy.npz')\n\n"
    "# 2. Define input case: [T, log10(strain_rate), density, shear_modulus]\n"
    "X_case = np.array([[100.0, -4.0, 2619.0, 24541.0]])\n\n"
    "# 3. Predict full 120-point flow-stress curve (0.221 ms)\n"
    "curve = runtime.predict(X_case)[0]\n"
    "print(f'Curve shape: {curve.shape}')  # (120,)\n\n"
    "# 4. Query stress at a specific strain point (e.g., E11 = 0.05)\n"
    "stress_at_point = np.interp(0.05, runtime.strain, curve)\n"
    "print(f'Flow Stress at E11=0.05: {stress_at_point:.4f} (inferred units)')\n"
)
add_code_block(code_example)

# ----------------- 8. REPRODUCIBILITY -----------------
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
add_bullet("reports/model_verification_20261025.json (Audit results and metrics)")
add_bullet("reports/final_training_reproduction_20261025.json (Refit timing and weight parity)")
add_bullet("reports/query_runtime_benchmark_20261025.json (Latency and file size measurements)")

# ----------------- 9. VIVA DEFENSE Q&A -----------------
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
    add_callout_box([
        (q, "Oral Defense Question: ", True),
        (a, "Verified Answer: ", False)
    ], bg_hex="F8FAFC", border_hex="0F172A", border_sz="16")

# ----------------- SAVE & CONVERT -----------------

PROJECT_FILES.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

out_docx_project = PROJECT_FILES / "model_guide.docx"
out_docx_reports = REPORTS_DIR / "model_guide.docx"

doc.save(out_docx_project)
doc.save(out_docx_reports)
print("Saved DOCX successfully:", out_docx_project)

# Convert to true binary .doc using LibreOffice
cmd_doc = f"libreoffice --headless --convert-to doc \"{out_docx_project}\" --outdir \"{PROJECT_FILES}\""
subprocess.run(cmd_doc, shell=True, check=True)

cmd_doc_rep = f"libreoffice --headless --convert-to doc \"{out_docx_reports}\" --outdir \"{REPORTS_DIR}\""
subprocess.run(cmd_doc_rep, shell=True, check=True)
print("Saved DOC successfully in project files/ and reports/")

# Also generate matched PDF from DOCX
cmd_pdf = f"libreoffice --headless --convert-to pdf \"{out_docx_project}\" --outdir \"{PROJECT_FILES}\""
subprocess.run(cmd_pdf, shell=True, check=True)

cmd_pdf_rep = f"libreoffice --headless --convert-to pdf \"{out_docx_reports}\" --outdir \"{REPORTS_DIR}\""
subprocess.run(cmd_pdf_rep, shell=True, check=True)
print("Saved PDF successfully in project files/ and reports/")
