"""Build presentation/JC-PINN.pptx (16:9, with speaker notes) from the figures and the saved run.

Numbers come from report/numbers.json (written by scripts/write_latex_numbers.py); figures from figures/.
Run from the repository root:  python scripts/build_deck.py
Optional PDF export:  soffice --headless --convert-to pdf --outdir presentation presentation/JC-PINN.pptx
"""
import json
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'
N = json.loads((ROOT / 'report/numbers.json').read_text())
N = {k: v.replace('{,}', ',') for k, v in N.items()}

INK, MUTED, BLUE, AMBER, RULE, PALE = (RGBColor.from_string(c) for c in ('18212B', '5B6878', '1D5EA8', 'A8620E', 'D5DCE4', 'EEF3F9'))
FONT = 'Calibri'
W, H = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]


def text(slide, x, y, w, h, runs, size=20, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.1):
    """runs: str, or list of paragraphs; a paragraph is a str or a list of (text, {bold,color,size}) pieces."""
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    paras = [runs] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        pieces = [(para, {})] if isinstance(para, str) else para
        for t, style in pieces:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name, f.size = FONT, Pt(style.get('size', size))
            f.bold = style.get('bold', bold)
            f.italic = style.get('italic', False)
            f.color.rgb = style.get('color', color)
            if style.get('sup'):
                r._r.get_or_add_rPr().set('baseline', '30000')
    return box


def bullets(slide, x, y, w, h, items, size=19):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(9)
        p.line_spacing = 1.05
        pieces = [(item, {})] if isinstance(item, str) else item
        r = p.add_run()
        r.text = '•  '
        r.font.name, r.font.size, r.font.color.rgb = FONT, Pt(size), BLUE
        for t, style in pieces:
            r = p.add_run()
            r.text = t
            r.font.name, r.font.size = FONT, Pt(style.get('size', size))
            r.font.bold = style.get('bold', False)
            r.font.color.rgb = style.get('color', INK)
    return box


def picture(slide, name, x, y, w, h):
    """Place figures/<name>.png inside the box, keeping its aspect ratio, centred."""
    path = FIG / f'{name}.png'
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = int(iw * scale), int(ih * scale)
    slide.shapes.add_picture(str(path), x + (w - pw) // 2, y + (h - ph) // 2, pw, ph)


def slide(title, kicker=None, notes=''):
    s = prs.slides.add_slide(BLANK)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.18), H)
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()
    if kicker:
        text(s, Inches(0.6), Inches(0.35), Inches(12), Inches(0.4), kicker.upper(), size=13, color=BLUE, bold=True)
    text(s, Inches(0.6), Inches(0.68), Inches(12.2), Inches(0.9), title, size=32, bold=True)
    line = s.shapes.add_connector(1, Inches(0.6), Inches(1.55), Inches(12.73), Inches(1.55))
    line.line.color.rgb = RULE
    num = len(prs.slides)
    text(s, Inches(12.2), Inches(7.0), Inches(0.9), Inches(0.35), str(num), size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    text(s, Inches(0.6), Inches(7.0), Inches(8), Inches(0.35), 'JC-PINN  ·  Team 8', size=11, color=MUTED)
    s.notes_slide.notes_text_frame.text = notes
    return s


def stat(s, x, y, value, label, color=BLUE, w=Inches(2.9)):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, Inches(1.5))
    card.adjustments[0] = 0.08
    card.fill.solid()
    card.fill.fore_color.rgb = PALE
    card.line.fill.background()
    text(s, x, y + Inches(0.12), w, Inches(0.75), value, size=34, bold=True, color=color, align=PP_ALIGN.CENTER)
    text(s, x + Inches(0.1), y + Inches(0.85), w - Inches(0.2), Inches(0.6), label, size=13, color=MUTED, align=PP_ALIGN.CENTER)


L, TOP, FULLW, BODYH = Inches(0.6), Inches(1.8), Inches(12.13), Inches(5.0)

# 1. Title ------------------------------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
bg.fill.solid()
bg.fill.fore_color.rgb = INK
bg.line.fill.background()
text(s, Inches(0.9), Inches(1.6), Inches(11.5), Inches(0.5), 'MULTISCALE MODELLING OF MATERIALS USING MACHINE LEARNING', size=14, color=RGBColor(0x8F, 0xB8, 0xE8), bold=True)
text(s, Inches(0.9), Inches(2.2), Inches(11.5), Inches(1.4), 'JC-PINN', size=66, bold=True, color=RGBColor(255, 255, 255))
text(s, Inches(0.9), Inches(3.45), Inches(11.5), Inches(1.4),
     'Our customised Johnson–Cook equation as the governing law of a neural material model for AM AlSi10Mg',
     size=26, color=RGBColor(0xDD, 0xE4, 0xEC))
text(s, Inches(0.9), Inches(5.6), Inches(11), Inches(0.5), 'Team 8  ·  November 2026', size=16, color=RGBColor(0xA9, 0xB6, 0xC4))
s.notes_slide.notes_text_frame.text = (
    'We built a material model for additively manufactured AlSi10Mg whose governing law is our own Equation 1, '
    'a customised Johnson–Cook equation. A small neural network corrects what the equation cannot capture. '
    'I will show the data, why the equation alone is not enough, how the model is built and trained, how we chose it '
    'without looking at the test set, and how it scored.')

# 2. The question -----------------------------------------------------------------------------------------
s = slide('Can Equation 1 govern an ML material model?', 'The question',
          'The bracket study needs material curves at any temperature, strain rate and porosity. Pure data-driven models fit '
          'the simulations but know no physics. Our question: can our own Johnson–Cook form serve as the governing law of the model, '
          'and what does it gain or cost? We answer it with a locked, once-scored test.')
bullets(s, L, TOP, Inches(6.6), BODYH, [
    'The wing-rib bracket study needs AlSi10Mg stress curves at any temperature, strain rate and porosity',
    'Data-driven MLPs fit the simulations, but carry no physics',
    [('Goal: ', {'bold': True}), ('use our customised Johnson–Cook law (Equation 1) as the backbone, and learn only what it misses', {})],
    [('Honest test: ', {'bold': True}), ('choose on training data only, lock, then score the 37 test cases once', {})],
])
stat(s, Inches(7.9), Inches(2.0), '73', 'simulations supplied (of 108 planned)')
stat(s, Inches(7.9), Inches(3.75), '36 / 37', 'train / test cases, split by simulation', color=INK)
stat(s, Inches(10.0) + Inches(0.9), Inches(2.0), '120', 'strain points per curve', color=INK, w=Inches(1.85))
stat(s, Inches(10.0) + Inches(0.9), Inches(3.75), '5', 'inputs: T, rate, ρ, G, E11', color=INK, w=Inches(1.85))

# 3. Data -------------------------------------------------------------------------------------------------
s = slide('Every curve softens, and the shape changes with condition', 'Data',
          'These are the 36 training curves: von Mises stress against axial strain E11. All of them soften. Softening grows with '
          'temperature: at 30 °C the stress at 10 % strain is about 0.7 of its start, at 200 °C about 0.2, and case 60 collapses '
          'to 0.06. Coverage is uneven: 27, 27 and 19 cases at 30, 100 and 200 °C, and none at 300 °C, and none will be added. '
          'The units, degrees C, per second, MPa and kilograms per cubic metre, were confirmed by the user, but we never saw the '
          "generator's documentation.")
picture(s, 'fig_data', L, TOP, FULLW, Inches(3.9))
text(s, L, Inches(5.85), FULLW, Inches(1.0),
     'Coverage: 27 cases at 30 °C, 27 at 100 °C, 19 at 200 °C, none at 300 °C  ·  rate 1e-5 to 1e-3 s⁻¹  ·  ρ 2488–2700  ·  G 23314–25300 MPa (units confirmed by the user; no generator documentation)',
     size=15, color=MUTED, align=PP_ALIGN.CENTER)

# 4. Equation 1 -------------------------------------------------------------------------------------------
s = slide('Equation 1: our customised Johnson–Cook law', 'Governing equation',
          'Five factors: strain, rate, temperature, shear modulus and porosity. The strain term has a minus sign because the data soften. '
          'Strain is E11; the rate enters as a ratio to 1e-5; T star uses 30 and 600 °C; G0 is 25300 MPa; porosity is one minus density over 2700. '
          'B is written as A beta over 0.1 to the n so the strain term stays positive, and C, q, r are non-negative so no trend has the wrong sign.')
sup = {'sup': True}
text(s, L, Inches(1.95), FULLW, Inches(0.9), [[
    ('σ = [A − B·ε', {}), ('n', sup), ('] · [1 + C ln ε̇*] · [1 − T*', {}), ('m', sup), ('] · [G/G₀]', {}), ('q', sup),
    (' · [1 − φ]', {}), ('r', sup)]], size=34, bold=True, color=AMBER, align=PP_ALIGN.CENTER)
rows = [('ε', 'axial strain E11 (no elastic segment exists)'), ('ε̇*', 'ε̇ / 10⁻⁵ s⁻¹'), ('T*', '(T − 30) / (600 − 30)'),
        ('G₀', '25300 MPa'), ('φ', '1 − ρ / 2700 per case (0, 3, 7.85 % in data; study point 4 %)'),
        ('bounds', 'B = A·β/0.1ⁿ, 0 ≤ β ≤ 0.99;  C, q, r ≥ 0')]
tbl = s.shapes.add_table(len(rows), 2, Inches(2.2), Inches(3.1), Inches(8.9), Inches(3.4)).table
tbl.columns[0].width, tbl.columns[1].width = Inches(1.6), Inches(7.3)
for i, (a, b) in enumerate(rows):
    for j, v in enumerate((a, b)):
        c = tbl.cell(i, j)
        c.text = v
        c.fill.solid()
        c.fill.fore_color.rgb = PALE if i % 2 == 0 else RGBColor(255, 255, 255)
        para = c.text_frame.paragraphs[0]
        para.runs[0].font.size, para.runs[0].font.name = Pt(17), FONT
        para.runs[0].font.bold = j == 0
        para.runs[0].font.color.rgb = INK

# 5. Why it fails alone -----------------------------------------------------------------------------------
s = slide('Alone, Equation 1 cannot bend its curves', 'Why a correction is needed',
          f"Equation 1 is a product of separate factors, so temperature or rate can only scale a curve, not reshape it. Calibrated alone it "
          f"misses by {N['EqCV']} MPa in cross-validation and {N['TestEq']} MPa on the test set. This is a property of the separable form, "
          f"not a fitting failure.")
picture(s, 'fig_eq1_fail', L, TOP, FULLW, Inches(3.8))
stat(s, Inches(1.6), Inches(5.55), f"{N['EqCV']} MPa", 'case-CV error, Equation 1 alone', color=AMBER, w=Inches(3.2))
stat(s, Inches(5.05), Inches(5.55), f"{N['TestEq']} MPa", 'test error, Equation 1 alone', color=AMBER, w=Inches(3.2))
stat(s, Inches(8.5), Inches(5.55), 'separable', 'conditions only rescale the curve', color=INK, w=Inches(3.2))

# 6. Model ------------------------------------------------------------------------------------------------
s = slide('The JC-PINN: Equation 1 × a learned correction', 'Model',
          'The prediction is Equation 1 times exp of delta. Delta comes from a 5-16-16-1 tanh network with 385 weights. Its output layer '
          'starts at zero, so before training the model is exactly Equation 1. Exp of delta is a correction factor and keeps stress positive. '
          'Five copies with different seeds are averaged in log space.')
picture(s, 'fig_architecture', L, TOP, Inches(8.2), Inches(3.6))
bullets(s, Inches(8.95), Inches(1.95), Inches(3.9), Inches(4.8), [
    [('prediction = σ_JC · exp(δ)', {'bold': True, 'color': BLUE})],
    f"δ: 5→16→16→1 tanh, {N['Params']} weights",
    'Output layer starts at 0: the untrained model is Equation 1',
    'exp(δ) = 0.9 means 10 % below Equation 1',
    'Geometric mean of 5 copies (seeds 0–4)',
], size=17)
text(s, L, Inches(5.65), Inches(8.2), Inches(1.1),
     [[('Loss  = ', {'bold': True}), ('data misfit  +  λ · physics residual at ' + N['Colloc'] + ' collocation points  +  weight decay', {})],
      [('Physics residuals tested: ', {'bold': True}), ('level (stay near Eq. 1) and trend (match its sensitivities, by autograd)', {})]],
     size=15, color=INK)

# 7. Training ---------------------------------------------------------------------------------------------
s = slide('Training: start from the law, learn the shape', 'Training',
          f"Each copy runs {N['AdamSteps']} Adam steps at learning rate {N['AdamLR']}, then up to {N['LbfgsIter']} L-BFGS iterations. "
          'On the right, a 200 °C training case: at step 0 the model is Equation 1; by step 400 it has learned the shape; the final curve '
          'matches the simulation. Weight decay alpha = 1 was fixed beforehand on training folds, because a weaker value let exp delta blow up.')
picture(s, 'fig_training', L, TOP, Inches(8.6), Inches(4.4))
bullets(s, Inches(9.35), Inches(2.0), Inches(3.5), Inches(4.6), [
    f"Adam: {N['AdamSteps']} steps, lr {N['AdamLR']}",
    f"then L-BFGS: ≤ {N['LbfgsIter']} iterations",
    f"Weight decay α = {N['Alpha']} (fixed on training folds)",
    'PyTorch, CPU; deterministic seeds',
], size=17)

# 8. Selection --------------------------------------------------------------------------------------------
s = slide('Choosing the setting without touching the test set', 'Selection',
          f"We compared {N['Settings']} settings: no physics, level and trend residuals at several weights, each with frozen or jointly "
          f"fitted constants, three seeds each. Score = half of case cross-validation plus the mean error when each of nine temperature/rate "
          f"groups is hidden. The winner was no physics loss with joint constants, score {N['SelScore']}. Every stronger physics weight was worse. "
          'The model was then fingerprinted and locked before any test curve was read.')
picture(s, 'fig_selection', L, TOP, Inches(8.9), Inches(4.9))
bullets(s, Inches(9.7), Inches(2.0), Inches(3.2), Inches(4.8), [
    [('Score = ½ (case CV + hidden groups)', {'bold': True})],
    [('Selected: ', {}), ('no physics loss, joint constants', {'bold': True, 'color': BLUE})],
    f"CV {N['SelCV']}  ·  groups {N['SelGroups']}  ·  score {N['SelScore']}",
    'Locked (SHA-256) before the test set was read',
], size=16)

# 9. Headline result --------------------------------------------------------------------------------------
s = slide('Test result: scored once, after the lock', 'Results',
          f"On the 37 test cases the mean curve error is {N['TestMean']} MPa, median {N['TestMedian']}, worst {N['TestWorst']} at case "
          f"{N['TestWorstCase']}. R squared is {N['TestRsq']}; {N['TestWithinOne']} percent of the {N['TestPoints']} points are within one MPa. "
          f"That is {N['Improvement']} times better than Equation 1 alone.")
stat(s, Inches(0.75), Inches(2.0), f"{N['TestMean']} MPa", 'mean curve RMSE (37 cases)')
stat(s, Inches(3.85), Inches(2.0), N['TestRsq'], 'R² over ' + N['TestPoints'] + ' points')
stat(s, Inches(6.95), Inches(2.0), N['TestWithinOne'] + ' %', 'of points within ±1 MPa')
stat(s, Inches(10.05), Inches(2.0), N['Improvement'] + '×', 'more accurate than Equation 1 alone', color=AMBER, w=Inches(2.6))
picture(s, 'fig_test_examples', L, Inches(3.75), FULLW, Inches(3.15))

# 10. All cases -------------------------------------------------------------------------------------------
s = slide('Accurate and precise: no bias, little spread', 'Results',
          f"Errors are not systematic: mean signed error {N['TestBias']} MPa, {N['CasesHigh']} cases slightly high and {N['CasesLow']} low. "
          f"The five copies agree to {N['SpreadMean']} MPa on average. Training fit {N['TrainFit']} versus test {N['TestMean']}, so no over-fitting. "
          'The eight worst cases all sit at 30 °C and 1e-4, which has only one training case.')
picture(s, 'fig_test_points', L, TOP, FULLW, Inches(3.4))
bullets(s, Inches(1.2), Inches(5.35), Inches(11.5), Inches(1.6), [
    f"Bias {N['TestBias']} MPa  ·  {N['CasesHigh']} cases slightly high, {N['CasesLow']} low: no systematic error",
    f"The 5 copies agree to {N['SpreadMean']} MPa (max {N['SpreadMax']})  ·  training fit {N['TrainFit']} vs test {N['TestMean']}: no over-fitting",
    'Weakest condition: 30 °C, 1e-4 s⁻¹ (8 test cases, only 1 training case); all 37 curves are in the report',
], size=17)

# 11. Comparison ------------------------------------------------------------------------------------------
s = slide('Where it stands against the alternatives', 'Comparison',
          f"On the random test split the purely data-driven MLPs are more precise: {N['SingleTest']} and {N['EnsTest']} MPa. The JC-PINN beats "
          f"Equation 1 alone on all 37 cases and the curve lookup on {N['WinsLookup']}. The harder test is unseen conditions: hiding whole groups, "
          f"the JC-PINN scores {N['SelGroups']} against {N['SingleGroups']} for the single MLP, about half.")
picture(s, 'fig_comparison', L, TOP, Inches(6.0), Inches(2.6))
picture(s, 'fig_groups', Inches(6.75), TOP, Inches(6.0), Inches(2.8))
bullets(s, L, Inches(4.75), FULLW, Inches(2.1), [
    f"Random split: data-driven MLPs are more precise ({N['SingleTest']} and {N['EnsTest']} MPa)",
    f"JC-PINN beats Equation 1 alone on {N['WinsEq']}/37 cases and the curve lookup on {N['WinsLookup']}/37",
    [('Unseen conditions: ', {'bold': True}), (f"JC-PINN {N['SelGroups']} vs single MLP {N['SingleGroups']} MPa, about half the error", {})],
], size=17)

# 12. Control ---------------------------------------------------------------------------------------------
s = slide('The control: what does Equation 1 actually add?', 'Honest check',
          f"After the lock we trained the same network with Equation 1 replaced by a constant. It was better on every measure: test "
          f"{N['CtrlTest']} against {N['TestMean']}, groups {N['CtrlGroups']} against {N['SelGroups']}. So on these data the equation's separable "
          'form does not add accuracy. What it adds is structure: named constants, correct trends and a physically sensible starting point. '
          'We report this rather than hide it.')
tbl = s.shapes.add_table(4, 4, Inches(0.9), Inches(2.0), Inches(7.2), Inches(2.4)).table
data = [('', 'Case CV', 'Groups', 'Test'), ('JC-PINN', N['SelCV'], N['SelGroups'], N['TestMean']),
        ('Same network, Eq. 1 off', N['CtrlCV'], N['CtrlGroups'], N['CtrlTest']), ('Equation 1 alone', N['EqCV'], N['EqGroups'], N['TestEq'])]
for i, row in enumerate(data):
    for j, v in enumerate(row):
        c = tbl.cell(i, j)
        c.text = v
        c.fill.solid()
        c.fill.fore_color.rgb = INK if i == 0 else (PALE if i % 2 else RGBColor(255, 255, 255))
        r = c.text_frame.paragraphs[0].runs[0] if v else None
        if r:
            r.font.size, r.font.name = Pt(17), FONT
            r.font.bold = i == 0 or j == 0
            r.font.color.rgb = RGBColor(255, 255, 255) if i == 0 else INK
        c.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT
bullets(s, Inches(8.6), Inches(2.0), Inches(4.2), Inches(4.8), [
    [('Equation 1 adds structure, not accuracy', {'bold': True, 'color': BLUE})],
    'Named constants for strain, rate, temperature, modulus, porosity',
    'Correct trend signs everywhere in 30–200 °C',
    'Starts from a physically sensible law',
], size=17)
text(s, Inches(0.9), Inches(4.75), Inches(7.2), Inches(1.6),
     f"Fitted constants: A {N['PinnA']}, B {N['PinnB']}, n {N['Pinnn']}, C {N['PinnC']}, m {N['Pinnm']}, q {N['Pinnq']}, r ≈ 0. "
     'The control was run after the lock and not used for selection.', size=15, color=MUTED)

# 13. Improvement screen ----------------------------------------------------------------------------------
s = slide('Could it be better? We screened, then kept it', 'Improvement screen',
          f"On training cases only: longer training gave {N['ScrIterLong']}, weaker weight decay {N['ScrAlphaLow']}, a wider network "
          f"{N['ScrWide']}, all worse than {N['SelCV']}. Even fitting A minus B eps to the n to each curve separately leaves {N['FloorJCMean']} MPa, "
          'so the power-law shape is a floor. Bounded and additive corrections also scored worse. We submit the locked model unchanged.')
tbl = s.shapes.add_table(6, 2, Inches(0.9), Inches(2.0), Inches(7.4), Inches(3.9)).table
tbl.columns[0].width, tbl.columns[1].width = Inches(5.2), Inches(2.2)
data = [('Variant (training cases only)', 'Result'), ('Locked model, case CV', N['SelCV']), ('8000 L-BFGS iterations', N['ScrIterLong']),
        ('Weight decay α = 0.3', N['ScrAlphaLow']), ('Wider 32–32 network', N['ScrWide']),
        ('Bounded correction, score', N['ScrBoundedScore'] + ' vs ' + N['SelScore'])]
for i, row in enumerate(data):
    for j, v in enumerate(row):
        c = tbl.cell(i, j)
        c.text = v
        c.fill.solid()
        c.fill.fore_color.rgb = INK if i == 0 else (PALE if i % 2 else RGBColor(255, 255, 255))
        r = c.text_frame.paragraphs[0].runs[0]
        r.font.size, r.font.name, r.font.bold = Pt(16), FONT, i in (0, 1)
        r.font.color.rgb = RGBColor(255, 255, 255) if i == 0 else INK
bullets(s, Inches(8.8), Inches(2.0), Inches(4.0), Inches(4.8), [
    [('Strain-law floor: ', {'bold': True}), (f"A − Bεⁿ fitted per curve still leaves {N['FloorJCMean']} MPa (cubic: {N['FloorCubicMean']})", {})],
    'None of the variants beat the locked model',
    [('Decision: ', {'bold': True}), ('submit the locked model unchanged', {'color': BLUE, 'bold': True})],
], size=17)

# 14. Study point -----------------------------------------------------------------------------------------
s = slide('Using it: curves at the 4 % porosity study point', 'Application',
          'At the project study point, porosity 4 percent, density 2592 and G 24541, the model gives these curves. The ANSYS bridge in the '
          'bracket folder writes such a curve as a material card. The 300 °C curves are dashed: there are no data there and no physics '
          'penalty acts, so they are unvalidated extrapolation.')
picture(s, 'fig_study_point', L, TOP, FULLW, Inches(4.1))
text(s, L, Inches(6.05), FULLW, Inches(0.8),
     'φ = 4 % → ρ = 2592 kg m⁻³, G = 24541 MPa  ·  dashed 300 °C curves have no data and are unvalidated  ·  bracket/tools/ansys_material_bridge.py writes a material card',
     size=15, color=MUTED, align=PP_ALIGN.CENTER)

# 14b. Porosity ------------------------------------------------------------------------------------------
s = slide('How porosity acts: small, consistent, carried by the network', 'Porosity',
          f"Porosity enters only through density. In all {N['PorPairsLower']} pairs of cases that differ only in density, lower density "
          f"gives lower stress, but the effect is small: {N['PorData']} percent from zero to 7.85 percent porosity, growing from "
          f"{N['PorDataThirty']} at 30 °C to {N['PorDataTwoHundred']} at 200 °C. Equation 1's porosity exponent fitted to zero because this "
          f"0.3 MPa effect is buried under its 10 MPa misfit; the data imply about {N['PorImpliedR']}. The correction network reproduces it: "
          f"{N['PorModel']} against {N['PorData']} percent, correlation {N['PorFullCorr']}. G acts about {N['PorRatio']} times more strongly, "
          'so for a real bracket the porosity effect depends mainly on how G falls with porosity, which the data do not define.')
picture(s, 'fig_porosity', L, TOP, Inches(7.9), Inches(3.6))
bullets(s, Inches(8.75), Inches(1.95), Inches(4.1), Inches(4.9), [
    f"All {N['PorPairsLower']}/{N['PorPairs']} density-only pairs: lower density → lower stress",
    f"φ 0 → 7.85 %: −{N['PorData']} % ({N['PorDataThirty']} % at 30 °C, {N['PorDataTwoHundred']} % at 200 °C)",
    [('Equation 1: ', {'bold': True}), (f"r fitted 0 (data imply ≈ {N['PorImpliedR']})", {})],
    [('JC-PINN: ', {'bold': True, 'color': BLUE}), (f"{N['PorModel']} % vs {N['PorData']} %, correlation {N['PorFullCorr']}", {})],
], size=16)
text(s, L, Inches(5.65), Inches(7.9), Inches(1.2),
     f"G acts about {N['PorRatio']}× more strongly, so for a real bracket the porosity effect depends mainly on the relation G(φ), "
     'which these simulations do not define.', size=15, color=MUTED)

sgn = lambda v: v.replace('-', '−')  # typographic minus for signed changes

# 14c. FE material and verification (post-hoc, model unchanged) ------------------------------------------------
s = slide('From model to finite-element material', 'After the lock',
          'After the lock, without refitting, we generated an Abaqus UMAT and an ANSYS USERMAT from the locked weights. Both are J2 plasticity '
          'with a radial return, and their flow stress is the JC-PINN prediction at the current plastic strain. Elasticity comes from G and an '
          f"assumed Poisson's ratio of 0.33. Offline, they reproduce the Python model to a relative error of {N['VerStressErr']}, with the "
          f"tangent to {N['VerTangentErr']}. Built into MAPDL 2024 R1, one element pulled to 12 percent strain matches the offline result to "
          f"{N['SeMaxDiff']} MPa at all {N['SePoints']} substeps, against a {N['SeTol']} MPa tolerance. The Abaqus UMAT has only been checked offline.")
bullets(s, L, TOP, Inches(6.3), BODYH, [
    [('Generated, not refitted: ', {'bold': True}), ('UMAT (Abaqus) and USERMAT (ANSYS) written from the locked weights', {})],
    'J2 plasticity, radial return, consistent tangent; flow stress = JC-PINN at the current plastic strain',
    'Elastic part from G and an assumed ν = 0.33; outside the data the routines flag, they do not clamp',
    [('Offline check: ', {'bold': True}), (f"stress {N['VerStressErr']}, slope {N['VerSlopeErr']}, tangent {N['VerTangentErr']} (relative)", {})],
], size=17)
stat(s, Inches(7.4), Inches(2.0), f"{N['SeMaxDiff']} MPa", f"MAPDL 2024 R1 single element vs offline ({N['SePoints']} substeps)", w=Inches(2.6))
stat(s, Inches(10.15), Inches(2.0), f"{N['SeSFinal']} MPa", f"final σ11 at ε11 = 0.12 (EQPS {N['SeEqpsFinal']})", color=INK, w=Inches(2.6))
stat(s, Inches(7.4), Inches(3.75), N['VerFlagChecks'] + ' / ' + N['VerFlagChecks'], 'range-flag cases set correctly', color=INK, w=Inches(2.6))
stat(s, Inches(10.15), Inches(3.75), 'offline', 'Abaqus UMAT checked only offline', color=AMBER, w=Inches(2.6))
text(s, Inches(7.4), Inches(5.5), Inches(5.35), Inches(1.3),
     'umat/verification.json  ·  umat/ansys_test/results_2026-11-17/', size=14, color=MUTED)

# 14d. Bracket and porosity --------------------------------------------------------------------------------------
s = slide('The bracket with the JC-PINN, and what density alone does', 'Bracket',
          f"This is the project's Workbench bracket, unchanged: {N['MeshElemCoarse']} SOLID186 elements, a fixed support, and an imposed "
          f"2 mm displacement, solved in MAPDL with three materials. The JC-PINN at the 4 percent study point peaks at {N['BrUsermatPeakkN']} kN, "
          f"then softens to {N['BrUsermatFinalkN']} kN. The Workbench EP card is a different material condition: it yields at 251 MPa and "
          f"hardens. It is a reference, not a validation. With G fixed, going from 0 to 7.85 percent porosity changes the peak by only "
          f"{N['PorDensPeakChangePct']} percent, matching the single-element {N['PorSeDensYieldPct']} percent. Per percent change, G acts about "
          f"{N['PorBrGOverDens']} times more strongly, and G of phi is unknown, so this is only the density part of the porosity effect.")
picture(s, 'fig_bracket', L, TOP, Inches(6.3), Inches(2.9))
picture(s, 'fig_bracket_porosity', Inches(6.95), TOP, Inches(5.8), Inches(2.9))
bullets(s, L, Inches(4.85), FULLW, Inches(2.1), [
    [('JC-PINN at φ = 4 %: ', {'bold': True, 'color': BLUE}),
     (f"peak {N['BrUsermatPeakkN']} kN at −{N['BrUsermatPeakUX']} mm, then softens to {N['BrUsermatFinalkN']} kN; EP card (different material) hardens to {N['BrEpFinalkN']} kN", {})],
    [('Density only, G fixed: ', {'bold': True}),
     (f"φ 0 → 7.85 % changes the peak by {sgn(N['PorDensPeakChangePct'])} % (single element: {sgn(N['PorSeDensYieldPct'])} %)", {})],
    [('G matters more: ', {'bold': True, 'color': AMBER}),
     (f"about {N['PorBrGOverDens']}× per percent; G(φ) is unknown, so this is the density part only", {})],
], size=16)

# 14e. Mesh dependence -------------------------------------------------------------------------------------------
s = slide('The softening makes the bracket result mesh dependent', 'Mesh study',
          f"We split every element 2 by 2 by 2, which gives {N['MeshElemFine']} elements with the same geometry, supports and load. This is a uniform "
          f"split, not a Workbench remesh. With the JC-PINN the peak force changes by {N['BrMeshPeakChangePct']} percent, and later forces by "
          f"{N['MeshForceMidChangePct']} and {N['MeshForceOneChangePct']} percent. The peak plastic strain rises from {N['MeshEqpsCoarse']} to "
          f"{N['MeshEqpsFine']}. The same split with the hardening EP card changes the force by at most {N['MeshEpMaxChangePct']} percent, so "
          'the softening causes it. Bracket forces after yield are specific to the mesh, not a converged strength. A regularised softening law is future work.')
picture(s, 'fig_mesh_ep', L, TOP, Inches(7.9), Inches(3.4))
bullets(s, Inches(8.75), Inches(1.95), Inches(4.1), Inches(4.9), [
    f"5 mm → 2.5 mm ({N['MeshElemCoarse']} → {N['MeshElemFine']} elements), uniform split",
    [('JC-PINN: ', {'bold': True, 'color': BLUE}),
     (f"peak {sgn(N['BrMeshPeakChangePct'])} %, later forces {sgn(N['MeshForceMidChangePct'])} / {sgn(N['MeshForceOneChangePct'])} %", {})],
    [('Hardening EP: ', {'bold': True}), (f"≤ {N['MeshEpMaxChangePct']} %, so the cause is the softening", {})],
    f"Peak plastic strain {N['MeshEqpsCoarse']} → {N['MeshEqpsFine']}, still rising",
], size=16)
text(s, L, Inches(5.5), Inches(7.9), Inches(1.4),
     [[('Bracket forces after yield are mesh-specific, not a converged strength.  ', {'bold': True, 'color': AMBER}),
       ('Future work: a regularised softening law. One material condition, small strain, ν = 0.33 assumed, nothing validated experimentally.', {})]],
     size=15, color=INK)

# 15. Limits ----------------------------------------------------------------------------------------------
s = slide('What we can and cannot claim', 'Limits',
          'The test is not blind: earlier stages explored those cases, though nothing in this model used them. Agreement is with simulations, '
          "not experiments. The units were confirmed by the user, but we never saw the generator's documentation. Nothing is validated above "
          '200 °C, and no such data will be added. Strain is total, not plastic. The porosity to modulus relation for a real part is not '
          'defined by the data. On the bracket, results after yield depend on the mesh. We do not predict critical flaw length.')
bullets(s, L, TOP, Inches(6.0), BODYH, [
    [('Can claim: ', {'bold': True, 'color': BLUE}), (f"{N['TestMean']} MPa on 37 locked test curves; correct trends in 30–200 °C", {})],
    [('Can claim: ', {'bold': True, 'color': BLUE}), ('about half the single-MLP error at unseen conditions', {})],
    [('Can claim: ', {'bold': True, 'color': BLUE}), ('independently verified and exactly reproducible', {})],
], size=18)
bullets(s, Inches(6.9), TOP, Inches(5.9), BODYH, [
    [('Cannot: ', {'bold': True, 'color': AMBER}), ('a blind test (cases explored earlier)', {})],
    [('Cannot: ', {'bold': True, 'color': AMBER}), ('experimental validity (units confirmed by the user, no generator documentation)', {})],
    [('Cannot: ', {'bold': True, 'color': AMBER}), ('anything above 200 °C', {})],
    [('Cannot: ', {'bold': True, 'color': AMBER}), ('plastic strain, a G(φ) law, or critical flaw length', {})],
    [('Cannot: ', {'bold': True, 'color': AMBER}), ('a mesh-converged bracket strength (softening)', {})],
], size=18)

# 16. Conclusion ------------------------------------------------------------------------------------------
s = slide('Conclusion', 'Summary',
          f"Equation 1 works as the governing law of a neural material model. The JC-PINN is {N['Improvement']} times better than the "
          'equation alone, about half the single-MLP error at unseen conditions, and keeps physically named constants. Physics residuals did '
          'not help here, and a law-free control was slightly more accurate, so the gain is structure, not accuracy. The locked model now '
          'runs as an ANSYS material on the bracket, where its softening makes results after yield mesh dependent. Next: a measured '
          'porosity–modulus relation, a regularised softening law, a fracture criterion, and experiments. Everything, including the notebook, '
          'videos and verifier, is in the repository.')
bullets(s, L, TOP, Inches(7.4), BODYH, [
    'Equation 1 works as the governing backbone; the network learns only the shape it misses',
    f"{N['TestMean']} MPa on 37 locked test curves, {N['Improvement']}× better than Equation 1 alone",
    f"About half the single-MLP error at unseen conditions ({N['SelGroups']} vs {N['SingleGroups']} MPa)",
    'Physics residuals did not help; the gain is structure and interpretability',
    'Runs as an ANSYS USERMAT on the bracket; results after yield are mesh dependent',
    [('Next: ', {'bold': True}), ('a measured G(φ), a regularised softening law, experiments', {})],
], size=18)
card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.5), Inches(2.0), Inches(4.25), Inches(4.4))
card.adjustments[0] = 0.05
card.fill.solid()
card.fill.fore_color.rgb = PALE
card.line.fill.background()
text(s, Inches(8.75), Inches(2.2), Inches(3.8), Inches(4.0), [
    [('In the repository', {'bold': True, 'color': BLUE, 'size': 18})],
    'Colab / Kaggle notebook',
    'Fully explained notebook',
    'Explainer and test-results videos',
    'Course report and IEEE paper',
    'Interactive model viewers',
    'Independent verifier',
], size=16, spacing=1.35)

out = ROOT / 'presentation/JC-PINN.pptx'
out.parent.mkdir(exist_ok=True)
prs.save(out)
print(f'wrote {out.relative_to(ROOT)} ({len(prs.slides)} slides)')
