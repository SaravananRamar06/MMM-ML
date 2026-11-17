"""Build teaching PDFs and offline viva cards; never modifies model results.

Install requirements-study.txt, then run with the project Python environment.
Saved numerical claims are substituted from report/numbers.json.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "exam-preparation"
OUTPUT = ROOT / "output"
PDF = OUTPUT / "pdf"
NUMBERS = json.loads((ROOT / "report" / "numbers.json").read_text(encoding="utf-8"))


def resolve(text: str) -> str:
    def number(match):
        return str(NUMBERS[match[1]]).replace("{,}", ",")
    return re.sub(r"\{\{(\w+)\}\}", number, text)


def inline(text: str) -> str:
    # Keep human-readable references in print without depending on repo-relative links.
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return html.escape(text).replace("`", "")


def build_pdf(path: Path, documents: list[str]):
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = "Study"
    styles.add(ParagraphStyle("StudyBody", fontName="Study", fontSize=10,
                              leading=14, spaceAfter=8, alignment=TA_LEFT))
    styles["Heading1"].fontName = "StudyBold"
    styles["Heading1"].fontSize = 22
    styles["Heading1"].leading = 27
    styles["Heading2"].fontName = "StudyBold"
    styles["Heading2"].fontSize = 15
    styles["Heading2"].leading = 20
    styles["Heading2"].spaceBefore = 14
    styles["Heading3"].fontName = "StudyBold"
    styles["Heading3"].fontSize = 11
    styles["Heading3"].leading = 15
    for key in ("Heading1", "Heading2", "Heading3"):
        styles[key].textColor = colors.HexColor("#17344a")
    story = []
    for index, document in enumerate(documents):
        if index:
            story.append(PageBreak())
        for block in document.split("\n\n"):
            block = block.strip()
            if not block:
                continue
            level = len(block) - len(block.lstrip("#"))
            if level in (1, 2, 3) and block[level:level+1] == " ":
                story.append(Paragraph(inline(block[level:].strip()), styles[f"Heading{level}"]))
                if block.startswith("## 9. Interpret"):
                    plot = ROOT / "bracket/ansys_usermat/mesh_2026-11-17/mesh_force_displacement.png"
                    from PIL import Image as PillowImage
                    with PillowImage.open(plot) as image:
                        width, height = image.size
                    story.append(Image(str(plot), width=170*mm, height=170*mm*height/width))
                    story.append(Paragraph("Saved two-mesh comparison: bracket reaction and local strain. Source: bracket/ansys_usermat/mesh_2026-11-17/. Numerical results, not validated strength.", styles["StudyBody"]))
            else:
                story.append(Paragraph(inline(block).replace("\n", "<br/>"), styles["StudyBody"]))
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Study", 8)
        canvas.setFillColor(colors.HexColor("#526473"))
        canvas.drawString(19*mm, 13*mm, "TEAM 8 | Examination preparation | 17 November 2026")
        canvas.drawRightString(191*mm, 13*mm, str(doc.page))
        canvas.restoreState()
    SimpleDocTemplate(str(path), pagesize=(210*mm, 297*mm),
                      rightMargin=19*mm, leftMargin=19*mm,
                      topMargin=19*mm, bottomMargin=22*mm,
                      title=path.stem.replace("-", " "), author="Team 8").build(
                          story, onFirstPage=footer, onLaterPages=footer)


def main():
    PDF.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "study").mkdir(exist_ok=True)
    font_root = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("Study", str(font_root / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("StudyBold", str(font_root / "arialbd.ttf")))
    documents = {}
    for name in ("study-handbook", "viva-bank", "team-workbook"):
        documents[name] = resolve((SOURCE / f"{name}.md").read_text(encoding="utf-8"))
        (OUTPUT / "study" / f"{name}.md").write_text(documents[name], encoding="utf-8")
        build_pdf(PDF / f"{name}.pdf", [documents[name]])
    references = (SOURCE / "README.md").read_text(encoding="utf-8")
    build_pdf(PDF / "complete-exam-preparation.pdf", [*documents.values(), references])

    cards = []
    topic = ""
    for block in re.split(r"(?=^## )", documents["viva-bank"], flags=re.M):
        heading = re.match(r"## (.+)", block)
        if heading:
            topic = heading[1]
        for match in re.finditer(r"^### ([^\n]+)\n\n(.*?)(?=^### |\Z)", block, re.M | re.S):
            cards.append({"topic": topic, "question": match[1], "answer": match[2].strip()})
    # Text is inserted with textContent, not interpreted as HTML.
    payload = json.dumps(cards, ensure_ascii=True).replace("<", "\\u003c")
    page = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Team 8: advanced viva practice</title>
<style>body{font:17px/1.65 system-ui;margin:0;background:#f4f6f7;color:#172f42}
main{max-width:900px;margin:auto;padding:36px 24px}h1{font-size:30px;line-height:1.2}
button,select{font:inherit;padding:8px 14px;margin:5px 5px 5px 0;border:1px solid #657783;background:white;color:inherit;border-radius:4px;cursor:pointer}
button:focus-visible,select:focus-visible{outline:3px solid #176d92}article{background:white;padding:26px;margin:20px 0;border-left:4px solid #176d92}
#answer{white-space:pre-wrap}small{color:#526473}#q{font-size:23px}button:disabled{opacity:.45;cursor:default}</style>
<main><small>TEAM 8 | LOCKED JC-PINN + ANSYS | 17 NOVEMBER 2026</small>
<h1>Defend the whole modelling chain</h1><p>Choose a topic. Answer aloud before revealing the guide, then handle the follow-up. Self-ratings are practice feedback, not an exam prediction.</p>
<label for="topic">Topic </label><select id="topic"><option value="">All topics</option></select>
<p id="progress" aria-live="polite"></p><article><small id="category"></small><h2 id="q"></h2>
<button id="reveal">Reveal answer</button><div id="answer" hidden></div></article>
<button id="again" disabled>Needs review</button><button id="know" disabled>Can explain</button>
<button id="previous">Previous</button><button id="next">Next</button><button id="shuffle">Shuffle</button><button id="reset">Reset ratings</button>
<p id="score" aria-live="polite"></p><small>Source: project preparation pack, saved numbers and repository evidence map. No network, no data upload. Ratings last for this page session. Every answer remains bounded by the simulation-only evidence, fixed-rate/strain mapping assumptions, non-blind test and mesh-dependent post-yield results.</small></main>
<script>const cards=PAYLOAD;let list=[...cards.keys()],position=0,ratings={};
const $=id=>document.getElementById(id);for(const topic of [...new Set(cards.map(c=>c.topic))]){const o=document.createElement('option');o.value=topic;o.textContent=topic;$('topic').append(o)}
function render(){const c=cards[list[position]];$('category').textContent=c.topic;$('q').textContent=c.question;$('answer').textContent=c.answer;$('answer').hidden=true;$('reveal').hidden=false;$('again').disabled=$('know').disabled=true;$('progress').textContent=`Question ${position+1} of ${list.length}`;$('previous').disabled=position===0;$('next').disabled=position===list.length-1;updateScore()}
function updateScore(){const vals=list.map(i=>ratings[i]);$('score').textContent=`This topic: ${vals.filter(v=>v==='know').length} can explain; ${vals.filter(v=>v==='again').length} need review; ${vals.filter(v=>!v).length} unassessed.`}
$('topic').onchange=()=>{list=cards.map((c,i)=>i).filter(i=>!$('topic').value||cards[i].topic===$('topic').value);position=0;render()};
$('reveal').onclick=()=>{$('answer').hidden=false;$('reveal').hidden=true;$('again').disabled=$('know').disabled=false};
for(const name of ['again','know'])$(name).onclick=()=>{ratings[list[position]]=name;updateScore()};
$('next').onclick=()=>{position++;render()};$('previous').onclick=()=>{position--;render()};
$('shuffle').onclick=()=>{for(let i=list.length-1;i>0;i--){let j=Math.floor(Math.random()*(i+1));[list[i],list[j]]=[list[j],list[i]]}position=0;render()};
$('reset').onclick=()=>{ratings={};updateScore()};render();</script></html>""".replace("PAYLOAD", payload)
    (OUTPUT / "study-practice.html").write_text(page, encoding="utf-8")
    print(f"Built 4 PDFs, 3 resolved Markdown guides and {len(cards)} viva cards.")


if __name__ == "__main__":
    main()
