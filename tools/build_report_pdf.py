#!/usr/bin/env python3
"""Build publication-grade academic HTML and PDF from report/report.tex.

Uses Chromium/Electron headless printToPDF with LibreOffice fallback.
Outputs:
  - project files/Final Course Report.pdf
  - project files/Final Course Report.html
  - report/report.html
  - report/report.pdf
"""
import base64
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TEX_FILE = ROOT / "report" / "report.tex"
OUT_HTML = ROOT / "project files" / "Final Course Report.html"
OUT_PDF = ROOT / "project files" / "Final Course Report.pdf"
LOCAL_HTML = ROOT / "report" / "report.html"
LOCAL_PDF = ROOT / "report" / "report.pdf"


def get_base64_img(path):
    mime = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def tex_to_academic_html(tex_content):
    # Locate figures
    fig_test = ROOT / "reports" / "retests" / "20261025T172218Z" / "test_curves.png"
    fig_loco = ROOT / "report" / "figures" / "condition_holdout_Svm.png"

    img_test_uri = get_base64_img(fig_test) if fig_test.exists() else "test_curves.png"
    img_loco_uri = get_base64_img(fig_loco) if fig_loco.exists() else "condition_holdout_Svm.png"

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Data-driven surrogate for the stress response of AlSi10Mg — Final Report</title>
<style>
  @page {{
    size: A4;
    margin: 20mm 20mm 20mm 20mm;
    @bottom-center {{
      content: counter(page);
    }}
  }}
  :root {{ color-scheme: light; }}
  body {{
    font-family: "Latin Modern Roman", "Times New Roman", "TeX Gyre Termes", Georgia, serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #111;
    background: #fff;
    margin: 0;
    padding: 0;
  }}
  .paper {{
    max-width: 780px;
    margin: 0 auto;
    padding: 30px 40px;
  }}
  .title-block {{
    text-align: center;
    margin-bottom: 24px;
  }}
  h1.title {{
    font-size: 18pt;
    font-weight: bold;
    margin: 0 0 6px 0;
    line-height: 1.25;
  }}
  .subtitle {{
    font-size: 13pt;
    color: #333;
    margin-bottom: 14px;
  }}
  .author {{
    font-size: 11pt;
    font-weight: 600;
    margin: 4px 0;
  }}
  .date {{
    font-size: 10pt;
    color: #555;
    margin: 2px 0 18px 0;
  }}
  .abstract-box {{
    margin: 18px 36px 24px 36px;
    padding: 12px 18px;
    font-size: 10pt;
    line-height: 1.45;
    text-align: justify;
    border-left: 2px solid #888;
    background: #fafafa;
  }}
  .abstract-title {{
    font-weight: bold;
    text-transform: uppercase;
    font-size: 9pt;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
    display: block;
    color: #222;
  }}
  h2.section {{
    font-size: 12.5pt;
    font-weight: bold;
    margin: 22px 0 8px 0;
    border-bottom: 1px solid #ccc;
    padding-bottom: 3px;
    page-break-after: avoid;
  }}
  h3.subsection {{
    font-size: 11pt;
    font-weight: bold;
    font-style: italic;
    margin: 14px 0 6px 0;
    page-break-after: avoid;
  }}
  p {{
    margin: 0 0 10px 0;
    text-align: justify;
    text-justify: inter-word;
  }}
  p.paragraph-lead {{
    margin-top: 10px;
  }}
  span.lead-title {{
    font-weight: bold;
    font-style: italic;
  }}
  ul {{
    margin: 6px 0 12px 20px;
    padding: 0;
  }}
  li {{
    margin-bottom: 5px;
    text-align: justify;
  }}
  .table-container {{
    margin: 18px auto;
    page-break-inside: avoid;
    text-align: center;
  }}
  table.booktabs {{
    margin: 6px auto;
    border-collapse: collapse;
    font-size: 10pt;
    width: 90%;
  }}
  table.booktabs th, table.booktabs td {{
    padding: 5px 12px;
    text-align: left;
  }}
  table.booktabs th.num, table.booktabs td.num {{
    text-align: right;
  }}
  table.booktabs thead tr:first-child th {{
    border-top: 2px solid #111;
    border-bottom: 1px solid #111;
    font-weight: 600;
  }}
  table.booktabs tbody tr:last-child td {{
    border-bottom: 2px solid #111;
  }}
  .caption {{
    font-size: 9.5pt;
    color: #222;
    margin: 6px auto 14px auto;
    max-width: 92%;
    text-align: justify;
    line-height: 1.35;
  }}
  .caption b {{
    font-weight: bold;
  }}
  .figure-container {{
    margin: 18px auto;
    text-align: center;
    page-break-inside: avoid;
  }}
  .figure-container img {{
    max-width: 95%;
    height: auto;
    border: 1px solid #eaeaea;
    border-radius: 2px;
  }}
  .references {{
    font-size: 9.5pt;
    line-height: 1.4;
    margin-top: 10px;
  }}
  .references ol {{
    padding-left: 24px;
    margin: 6px 0;
  }}
  .references li {{
    margin-bottom: 6px;
    text-align: left;
  }}
  code {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 9.5pt;
    background: #f4f4f4;
    padding: 1px 4px;
    border-radius: 3px;
  }}
  a {{ color: #0d47a1; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  @media print {{
    body {{ background: #fff; }}
    .paper {{ padding: 0; max-width: none; }}
    h2.section {{ page-break-after: avoid; }}
    .table-container, .figure-container {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
<div class="paper">

  <div class="title-block">
    <h1 class="title">Data-Driven Surrogate for the Stress Response of AlSi10Mg</h1>
    <div class="subtitle">Multiscale Modelling of an Additively Manufactured Wing-Rib Bracket — ML Component</div>
    <div class="author">Team 8</div>
    <div class="date">October 2026</div>
  </div>

  <div class="abstract-box">
    <span class="abstract-title">Abstract</span>
    We trained a small neural-network surrogate that predicts the von Mises stress response <i>S<sub>vm</sub></i> of AlSi10Mg along the operational strain <i>E</i><sub>11</sub>, given temperature, strain rate, density and shear modulus. The final predictor averages five 5–16–16–1 tanh networks (385 parameters each, 1,925 in total). On a fixed split of 37 held-out simulations, the mean per-curve RMSE is 0.0591 (worst 0.1133, case 45). Performance is much weaker when whole temperature/rate conditions are held out (mean 6.79), so the model closely reproduces the 37 related test curves, but its reliability at other input combinations, even inside the numerical ranges, is not established. Units are inferred, the held-out set is not fully blind, and the link from material porosity to the bracket's critical flaw length <i>C<sub>L</sub></i> has not been established. These limits are stated throughout.
  </div>

  <h2 class="section">1. Introduction and Scope</h2>
  <p>The wider project studies how porosity in an additively manufactured AlSi10Mg wing-rib bracket affects its structural integrity, expressed as the critical flaw length <i>C<sub>L</sub></i>: the largest defect the bracket can carry at its design stress before fracture. This report covers only the machine-learning component: a fast surrogate for the material's simulated stress response, intended to replace repeated material simulations inside a larger multiscale workflow. The structural (ANSYS) analysis is reported separately and is not covered here. Throughout, <i>C<sub>L</sub></i> means critical flaw length, not the aerodynamic coefficient of lift; the material data contains no flaw sizes or fracture-toughness values, so this report makes no <i>C<sub>L</sub></i> prediction.</p>

  <h2 class="section">2. Data</h2>
  <p>The professor's design matrix planned 108 simulations; 73 were available, containing 2,197,000 raw history rows. Temperature coverage is uneven: 27 cases at 30, 27 at 100, 19 at 200 and none at 300 (units inferred as °C). Each case also varies strain rate (10<sup>−5</sup> to 10<sup>−3</sup>, inferred s<sup>−1</sup>), density (2488.05 to 2700) and shear modulus <i>G</i> (23313.95 to 25300).</p>
  <p>The target is <i>S<sub>vm</sub></i> along operational <i>E</i><sub>11</sub>, not <i>S<sub>CAU11</sub></i>. Each history was interpolated onto a common grid of 120 <i>E</i><sub>11</sub> values from 0.0002 to 0.0999, so long, slow-rate runs do not dominate by row count. The histories do not show a conventional zero-stress elastic loading segment, so the surrogate should not be read as a constitutive law.</p>

  <h2 class="section">3. Method</h2>
  <h3 class="subsection">3.1 Split and Leakage Control</h3>
  <p>We used one fixed random split by simulation (seed 42): 36 training cases and 37 test cases, following the professor's requested 50/50 split as closely as 73 cases allow. All points from one simulation stay in one partition, and scalers were fitted on training cases only. The 36 training cases give 4,320 query points; these are not independent simulations. Earlier exploration used all the data, so the 37 test cases were excluded from final fitting but are <em>not</em> a fully blind holdout.</p>

  <h3 class="subsection">3.2 Model</h3>
  <p>Each network takes five inputs (temperature, log<sub>10</sub> strain rate, density, <i>G</i>, and the query <i>E</i><sub>11</sub>) and outputs one <i>S<sub>vm</sub></i> value. The architecture is 5–16–16–1 with tanh hidden layers and a linear output (385 parameters per network, 1,925 in total). Five networks with seeds 0–4 are trained with scikit-learn [1] using L-BFGS [2] and L2 penalty &alpha; = 0.001, and their predictions are averaged. This is a data-driven surrogate: there is no physics-informed loss term.</p>

  <h3 class="subsection">3.3 Model Selection</h3>
  <p>Candidates were compared on training-side evidence only: case-wise cross-validation and a condition holdout (whole temperature/rate groups removed). Table 1 lists the saved results. The query MLP was chosen because it had the best condition-holdout error, which matters most for use beyond the sampled conditions, while its case-CV error was competitive. A PCA + Gaussian-process [3] model was better on case CV but much worse when conditions were held out.</p>

  <div class="table-container">
    <table class="booktabs">
      <thead>
        <tr>
          <th>Candidate</th>
          <th class="num">Case CV</th>
          <th class="num">Condition holdout</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><strong>Query MLP (selected)</strong></td><td class="num"><strong>1.158</strong></td><td class="num"><strong>6.794</strong></td></tr>
        <tr><td>PCA + GP (6 components)</td><td class="num">0.664</td><td class="num">10.962</td></tr>
        <tr><td>MLP/GP blend</td><td class="num">0.867</td><td class="num">7.983</td></tr>
        <tr><td>Physics-style-input MLP</td><td class="num">1.536</td><td class="num">8.609</td></tr>
        <tr><td>PCA-coefficient MLP (4)</td><td class="num">2.269</td><td class="num">11.086</td></tr>
        <tr><td>PCA-coefficient MLP (6)</td><td class="num">2.004</td><td class="num">11.205</td></tr>
      </tbody>
    </table>
    <div class="caption"><b>Table 1:</b> Saved training-side comparison. Case CV is the mean curve RMSE over the 36 training cases; condition holdout is the unweighted mean of nine group-mean curve RMSEs (one per temperature/rate group), so it is neither a pooled nor a case-weighted error. Both are saved results, not a fresh evaluation of the delivered model.</div>
  </div>

  <h2 class="section">4. Results</h2>
  <p>On the 37 test cases the delivered model gives the errors in Table 2. Figure 1 shows two of them, including the worst.</p>

  <div class="table-container">
    <table class="booktabs" style="width:70%;">
      <thead>
        <tr>
          <th>Metric</th>
          <th class="num">Value (inferred stress units)</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Mean per-curve RMSE</td><td class="num">0.05909</td></tr>
        <tr><td>Median per-curve RMSE</td><td class="num">0.05057</td></tr>
        <tr><td>Worst curve RMSE (case 45)</td><td class="num">0.11331</td></tr>
        <tr><td>Mean per-curve MAE</td><td class="num">0.04900</td></tr>
        <tr><td>Pooled RMSE (all points)</td><td class="num">0.06486</td></tr>
        <tr><td>Largest single-point error</td><td class="num">0.28832</td></tr>
      </tbody>
    </table>
    <div class="caption"><b>Table 2:</b> Test-set errors of the final model (inferred stress units).</div>
  </div>

  <div class="figure-container">
    <img src="{img_test_uri}" alt="Test Curves">
    <div class="caption"><b>Figure 1:</b> Predicted vs. simulated <i>S<sub>vm</sub></i> for test cases 42 and 45, with residuals below (fresh retest, 25 Oct 2026). Case 45 is the worst of the 37 test curves.</div>
  </div>

  <p class="paragraph-lead"><span class="lead-title">Generalisation to new conditions.</span> Holding out whole temperature/rate groups raises the error to 6.79 (unweighted mean over the nine groups), about a hundred times the random-split error (Figure 2). The hardest group, 200 at 10<sup>−5</sup>, gives 23.53. Its only available case (60) lies in the training half. The low random-split error therefore mainly shows interpolation between closely related simulated conditions.</p>

  <div class="figure-container">
    <img src="{img_loco_uri}" alt="Condition Holdout Diagnostics" style="max-width:85%;">
    <div class="caption"><b>Figure 2:</b> Saved condition-holdout error of the selected query MLP by temperature/rate group (training half, &alpha; = 0.001), plotted from <code>runs/score/select_mlp_Svm.json</code> by <code>reports/plot_report_diagnostics.py</code>. This is a plot of saved diagnostics, not a fresh evaluation of the delivered model.</div>
  </div>

  <p class="paragraph-lead"><span class="lead-title">Worked example.</span> At temperature 100, rate 10<sup>−4</sup>, density 2619 and <i>G</i> = 24541, the model predicts 136.20912 at the start of the grid, 99.41858716 at <i>E</i><sub>11</sub> = 0.05 (interpolated) and 75.23194 at the end of the grid.</p>

  <p class="paragraph-lead"><span class="lead-title">Reproducibility.</span> A separate refit with the frozen settings reproduced every weight and prediction exactly in 17.26 s with no warnings. Thirteen model/parser/runtime unit tests and three live Model Studio tests pass. This is numerical reproducibility in the same environment, not physical, experimental or cross-platform validation.</p>

  <h2 class="section">5. Discussion</h2>
  <p>The surrogate is small, fast and reproducible, and closely reproduces the related test curves. Its reliability at other combinations of inputs is not established, even within the numerical ranges, because some groups are sparse and case 60 is irregular. Its main weakness is extrapolation: with 73 cases spread over three temperatures and three rates, some condition groups have very few cases, and errors grow sharply when a whole group is unseen. We propose adding simulations at the sparse and missing conditions (especially 200 and 300) as the first priority. We have not tested this against changing the model size.</p>
  <p>The model predicts stress along operational strain only. Turning it into an input for structural analysis needs the solver's stress/strain definitions, confirmed units and the receiving material model. Any ANSYS-format export remains an unvalidated template until those are confirmed. In particular, it must not invent a zero-origin elastic segment or label a total-strain curve as plastic strain.</p>

  <h2 class="section">6. Limitations and Open Questions</h2>
  <ul>
    <li>Units (MPa, °C, s<sup>−1</sup>) are inferred, not confirmed; the solver, material law and stress/strain definitions are unconfirmed.</li>
    <li>The 37 test cases were seen during earlier exploration, so the test score is not a fully independent generalisation estimate and may be optimistic.</li>
    <li>Whether density and modulus levels encode porosity, and the mapping if so, is unverified.</li>
    <li>There is no agreed <i>C<sub>L</sub></i> calculation (flaw geometry, fracture toughness <i>K</i><sub>IC</sub>, stress at the critical location), and the material &rarr; structure &rarr; critical-flaw coupling is undefined.</li>
    <li>The ANSYS analyses have not been checked against this report's material model; no transfer of predictions into ANSYS has been validated.</li>
    <li>Stronger generalisation claims need independent experimental data or new simulations.</li>
  </ul>

  <h2 class="section">7. Conclusion</h2>
  <p>A five-network MLP ensemble reproduces the simulated AlSi10Mg stress response with a mean test RMSE of 0.059 on related conditions and is exactly reproducible. Predictions at other input combinations, even within the simulated temperature, rate, density and modulus ranges, should be treated as unverified. Extending it to new conditions, porosity effects or critical-flaw-length prediction requires the missing definitions and data listed above.</p>

  <h2 class="section">Data Source</h2>
  <p>The simulation data were supplied by the course instructor (unpublished, Team 8 course project, 2026). They are not a public dataset; see <code>data/manifest.json</code> for the case list.</p>

  <h2 class="section">References</h2>
  <div class="references">
    <ol>
      <li>F. Pedregosa et al., &ldquo;Scikit-learn: Machine learning in Python,&rdquo; <i>J. Mach. Learn. Res.</i>, 12, 2825–2830, 2011. (Multilayer perceptron, Gaussian process and PCA implementations used.)</li>
      <li>D. C. Liu and J. Nocedal, &ldquo;On the limited memory BFGS method for large scale optimization,&rdquo; <i>Math. Program.</i>, 45, 503–528, 1989.</li>
      <li>C. E. Rasmussen and C. K. I. Williams, <i>Gaussian Processes for Machine Learning</i>, MIT Press, 2006.</li>
      <li>C. R. Harris et al., &ldquo;Array programming with NumPy,&rdquo; <i>Nature</i>, 585, 357–362, 2020.</li>
      <li>J. D. Hunter, &ldquo;Matplotlib: A 2D graphics environment,&rdquo; <i>Comput. Sci. Eng.</i>, 9(3), 90–95, 2007.</li>
    </ol>
  </div>

  <h2 class="section">Software and Evidence</h2>
  <p>Code: <code>src/</code> (data processing, models), <code>app/</code> (Model Studio). Evidence: <code>data/split.json</code>, <code>data/manifest.json</code>, <code>runs/score/</code>, <code>reports/retests/20261025T172218Z/</code>, <code>reports/model_verification_20261025.json</code>, <code>reports/final_training_reproduction_20261025.json</code>. Repository: <a href="https://github.com/SaravananRamar06/MMM-ML">https://github.com/SaravananRamar06/MMM-ML</a>.</p>

</div>
</body>
</html>"""
    return html


def compile_pdf(html_path, output_pdf_path):
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    temp_cjs = Path("/tmp/render_report_pdf.cjs")
    script = f"""
const {{ app, BrowserWindow }} = require('electron');
const fs = require('fs');

app.whenReady().then(async () => {{
  const win = new BrowserWindow({{ show: false, width: 1000, height: 1400 }});
  await win.loadURL('file://{html_path.resolve()}');
  // allow fonts and base64 images to settle
  await new Promise(r => setTimeout(r, 600));
  const pdf = await win.webContents.printToPDF({{
    pageSize: 'A4',
    marginsType: 0,
    printBackground: true
  }});
  fs.writeFileSync('{output_pdf_path.resolve()}', pdf);
  console.log('Electron PDF rendered successfully, size:', pdf.length);
  app.quit();
}});
"""
    temp_cjs.write_text(script, encoding="utf-8")
    try:
        res = subprocess.run(
            ["xvfb-run", "-a", "npx", "electron", str(temp_cjs)],
            cwd="/home/sarvn/Documents/AI-GroupChat",
            capture_output=True,
            text=True,
            timeout=25
        )
        if output_pdf_path.exists() and output_pdf_path.stat().st_size > 5000:
            return True, "Electron printToPDF"
    except Exception as exc:
        sys.stderr.write(f"Electron rendering failed: {exc}\n")

    # Fallback to headless LibreOffice
    res = subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", str(html_path), "--outdir", str(output_pdf_path.parent)],
        capture_output=True, text=True, timeout=30
    )
    generated = output_pdf_path.parent / (html_path.stem + ".pdf")
    if generated.exists():
        if generated != output_pdf_path:
            generated.replace(output_pdf_path)
        return True, "LibreOffice headless"
    return False, res.stderr


def main():
    if not TEX_FILE.exists():
        sys.exit(f"Source LaTeX file not found: {TEX_FILE}")

    tex_text = TEX_FILE.read_text(encoding="utf-8")
    html_content = tex_to_academic_html(tex_text)

    # Save HTML files
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html_content, encoding="utf-8")
    LOCAL_HTML.write_text(html_content, encoding="utf-8")
    print(f"Generated HTML: {OUT_HTML} & {LOCAL_HTML}")

    # Compile to PDF
    ok, engine = compile_pdf(OUT_HTML, OUT_PDF)
    if not ok:
        sys.exit(f"Failed to compile PDF: {engine}")
    
    # Copy to report/report.pdf as well
    LOCAL_PDF.write_bytes(OUT_PDF.read_bytes())
    print(f"Compiled PDF using {engine}: {OUT_PDF} ({OUT_PDF.stat().st_size} bytes)")
    print(f"Mirrored PDF to: {LOCAL_PDF}")


if __name__ == "__main__":
    main()
