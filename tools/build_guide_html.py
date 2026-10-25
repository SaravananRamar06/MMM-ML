import html
from pathlib import Path

ROOT = Path("/home/sarvn/Documents/MMM-ML")
text = (ROOT / "reports/model_guide.md").read_text(encoding="utf-8")
lines = text.split("\n")
out = []
in_code = False
in_table = False

for line in lines:
    if line.startswith("```"):
        in_code = not in_code
        if in_code:
            out.append("<pre><code>")
        else:
            out.append("</code></pre>")
        continue
    if in_code:
        out.append(html.escape(line) + "\n")
        continue
    if line.startswith("|") and "---" in line:
        continue
    if line.startswith("|"):
        cols = [c.strip() for c in line.strip("|").split("|")]
        if not in_table:
            out.append("<table><thead><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in cols) + "</tr></thead><tbody>")
            in_table = True
        else:
            out.append("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in cols) + "</tr>")
        continue
    elif in_table:
        out.append("</tbody></table>")
        in_table = False

    if line.startswith("# "):
        out.append(f"<h1>{html.escape(line[2:])}</h1>")
    elif line.startswith("## "):
        out.append(f"<h2>{html.escape(line[3:])}</h2>")
    elif line.startswith("### "):
        out.append(f"<h3>{html.escape(line[4:])}</h3>")
    elif line.startswith("#### "):
        out.append(f"<h4>{html.escape(line[5:])}</h4>")
    elif line.startswith("> "):
        out.append(f"<div class=\"box\">{html.escape(line[2:])}</div>")
    elif line.strip() == "---":
        out.append("<hr>")
    elif line.strip():
        out.append(f"<p>{html.escape(line)}</p>")

if in_table:
    out.append("</tbody></table>")

doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Technical Reference: AlSi10Mg Flow-Stress Neural Surrogate Model</title>
<style>
  body {{ font-family: 'Liberation Serif', 'Times New Roman', serif; font-size: 11pt; line-height: 1.5; margin: 0.6in; color: #111; }}
  h1 {{ font-size: 18pt; text-align: center; color: #0f172a; margin-bottom: 0.3em; }}
  h2 {{ font-size: 13pt; border-bottom: 1px solid #cbd5e1; padding-bottom: 3px; margin-top: 1.5em; color: #1e293b; }}
  h3 {{ font-size: 11.5pt; margin-top: 1.2em; color: #334155; }}
  h4 {{ font-size: 10.5pt; margin-top: 1em; color: #475569; }}
  p {{ margin: 0.6em 0; text-align: justify; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1.2em 0; font-size: 10pt; }}
  th, td {{ border: 1px solid #94a3b8; padding: 6px 10px; text-align: left; }}
  th {{ background-color: #f1f5f9; font-weight: bold; }}
  code {{ font-family: 'Liberation Mono', monospace; font-size: 9.5pt; background-color: #f8fafc; padding: 1px 3px; border: 1px solid #e2e8f0; }}
  pre {{ background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 3px solid #2563eb; padding: 10px; font-size: 9pt; font-family: 'Liberation Mono', monospace; overflow-x: auto; }}
  .box {{ background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 8px 12px; margin: 0.8em 0; }}
</style>
</head>
<body>
{''.join(out)}
</body>
</html>"""

(ROOT / "reports/model_guide.html").write_text(doc, encoding="utf-8")
print("HTML generated successfully.")
