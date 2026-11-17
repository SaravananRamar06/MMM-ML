"""Publish the audited Markdown lessons as a bookmarked, equation-rich textbook.

Uses ReportLab Platypus for book layout and Matplotlib MathText for mathematics.
Run after build_study_pack.py. No training or solver execution occurs.
"""
from pathlib import Path
import re
import html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                               PageBreak, Spacer, Image, KeepTogether, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents
from build_study_pack import ROOT, SOURCE, PDF, resolve

INK = colors.HexColor('#17344a')
PALE = colors.HexColor('#edf2f5')
WORK = ROOT / 'work' / 'textbook'
WIDTH = 156*mm


class Book(BaseDocTemplate):
    def afterFlowable(self, flow):
        if isinstance(flow, Paragraph) and flow.style.name in ('Chapter', 'Section'):
            level = 0 if flow.style.name == 'Chapter' else 1
            key = 'heading-' + str(self.seq.nextf('heading'))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flow.getPlainText(), key, level)
            self.notify('TOCEntry', (level, flow.getPlainText(), self.page, key))


def format_text(text):
    # Keep prose intact and distinguish code identifiers/file references.
    text = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\1 (\2)', text)
    parts = text.split('`')
    return ''.join('<font face="Mono" size="8.3">'+html.escape(p)+'</font>'
                   if i % 2 else html.escape(p) for i, p in enumerate(parts)).replace('&lt;br/&gt;', '<br/>')


def main():
    PDF.mkdir(exist_ok=True, parents=True)
    WORK.mkdir(exist_ok=True, parents=True)
    fonts = Path('C:/Windows/Fonts')
    for name, filename in [('Text','georgia.ttf'), ('TextBold','georgiab.ttf'),
                           ('TextItalic','georgiai.ttf'), ('Head','arial.ttf'),
                           ('HeadBold','arialbd.ttf'), ('Mono','consola.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(fonts/filename)))
    body = ParagraphStyle('Body', fontName='Text', fontSize=10.4, leading=15.4,
                          alignment=TA_LEFT, spaceAfter=9)
    chapter = ParagraphStyle('Chapter', fontName='HeadBold', fontSize=23, leading=29,
                             textColor=INK, spaceAfter=22, keepWithNext=True)
    section = ParagraphStyle('Section', fontName='HeadBold', fontSize=13, leading=18,
                             textColor=INK, spaceBefore=17, spaceAfter=9, keepWithNext=True)
    small = ParagraphStyle('Small', fontName='Head', fontSize=8, leading=11, spaceAfter=10)
    kicker = ParagraphStyle('Kicker', fontName='HeadBold', fontSize=10, leading=14,
                            textColor=INK, spaceAfter=12)
    story = []
    def para(text, style=body):
        return Paragraph(format_text(text), style)
    def box(title, text):
        t = Table([[para(title, kicker)], [para(text)]], colWidths=[WIDTH-8*mm])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),
                               ('LEFTPADDING',(0,0),(-1,-1),4*mm),
                               ('RIGHTPADDING',(0,0),(-1,-1),4*mm),
                               ('TOPPADDING',(0,0),(-1,0),4*mm),
                               ('BOTTOMPADDING',(0,-1),(-1,-1),3*mm)]))
        return t
    equation_no = 0
    def equation(tex):
        nonlocal equation_no
        equation_no += 1
        fig = plt.figure(figsize=(8, .8))
        fig.text(.5,.5,'$'+tex+'$', ha='center',va='center',fontsize=16)
        file = WORK/f'equation-{equation_no}.png'
        fig.savefig(file, dpi=300, bbox_inches='tight', pad_inches=.08, transparent=True)
        plt.close(fig)
        from PIL import Image as PI
        with PI.open(file) as im:
            w,h=im.size
        display_w = min(WIDTH-15*mm, w/300*72)
        row = Table([[Image(str(file), width=display_w, height=display_w*h/w),
                      para(f'({equation_no})', small)]], colWidths=[WIDTH-12*mm,12*mm])
        row.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
        story.extend([row,Spacer(1,7)])
    def figure(path, caption):
        from PIL import Image as PI
        with PI.open(ROOT/path) as im:
            w,h=im.size
        dw=WIDTH
        if dw*h/w > 92*mm:
            dw=92*mm*w/h
        story.append(KeepTogether([Image(str(ROOT/path), width=dw,height=dw*h/w),
                                     para(caption,small)]))

    # Cover, front matter and navigation.
    story += [Spacer(1,26*mm),para('TEAM 8 / STUDY EDITION',kicker),
              para('Materials, Finite Elements<br/>and Neural Constitutive Modelling',
                   ParagraphStyle('Cover',fontName='HeadBold',fontSize=30,leading=38,textColor=INK)),
              Spacer(1,10*mm),para('A project-based textbook for JC-PINN and the ANSYS wing-rib bracket'),
              Spacer(1,12*mm),para('Theory • derivations • worked examples • advanced viva • team presentation'),
              Spacer(1,20*mm),box('READ THE EVIDENCE AT ITS PROPER LEVEL',
              'A verified numerical implementation is not experimental validation. The selected physics-loss weight is zero; the test is not blind; the post-yield bracket response is mesh dependent.'),
              Spacer(1,15*mm),para('17 November 2026 | Model locked 7 November 2026',small),PageBreak()]
    story += [para('How to use this textbook',chapter),
              para('Read Part I as a connected account: material processing and effective properties lead to a constitutive law; local integration supplies stress and tangent; global equilibrium produces the structural response. Part II challenges that account through examiner follow-ups. Part III turns understanding into calculations and a team defence.'),
              para('This is a project-specific study edition, not an independently peer-reviewed textbook or a complete university course. General background is distinguished from measured, assumed and numerically verified project quantities. All saved performance numbers come from report/numbers.json.'),
              box('THREE LEVELS OF READING','First pass: explain the chain in words. Second pass: derive the displayed equations and redo the worked examples. Final pass: answer the viva questions closed-book and defend every assumption.'),
              Spacer(1,10*mm),para('Notation at a glance',section)]
    notation=[('Symbol','Meaning'),('sigma, s','Stress tensor and its deviatoric part'),
              ('q or sigma_eq','von Mises equivalent stress; q in the backbone is instead a fitted exponent'),
              ('p','Accumulated equivalent plastic strain'),('G, E, K, nu','Shear, Young\'s and bulk moduli; Poisson ratio'),
              ('phi, rho','Porosity fraction and density'),('delta','Neural logarithmic correction'),
              ('H','Derivative of flow stress with respect to p'),('lambda_L / lambda','Lame constant / physics-loss weight'),
              ('d, B, R','Nodal displacement vector, strain-displacement matrix, equilibrium residual')]
    table=Table([[para(a,small),para(b,small)] for a,b in notation],colWidths=[42*mm,114*mm])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),
                              ('LINEBELOW',(0,0),(-1,0),.5,INK),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story += [table,PageBreak(),para('Contents',chapter)]
    toc=TableOfContents()
    toc.levelStyles=[ParagraphStyle('Toc0',fontName='Head',fontSize=10,leading=15,spaceBefore=7),
                     ParagraphStyle('Toc1',fontName='Text',fontSize=9,leading=13,leftIndent=12)]
    story += [toc]

    equations={
      2:[r'\phi=1-\frac{\rho}{2700},\qquad G(\phi)=25300(1-\phi)'],
      3:[r'\mathbf{s}=\boldsymbol{\sigma}-\frac{\mathrm{tr}(\boldsymbol{\sigma})}{3}\mathbf{I},\qquad \sigma_{\rm eq}=\sqrt{\frac{3}{2}\mathbf{s}:\mathbf{s}}',
         r'E=2G(1+\nu),\qquad K=\frac{E}{3(1-2\nu)}'],
      4:[r'\int_V \boldsymbol{\varepsilon}(\mathbf{v}):\boldsymbol{\sigma}\,dV=\int_V\mathbf{v}\cdot\mathbf{b}\,dV+\int_{\Gamma_t}\mathbf{v}\cdot\bar{\mathbf{t}}\,dA',
         r'\mathbf{f}_{\rm int}=\int_V\mathbf{B}^{T}\boldsymbol{\sigma}\,dV,\qquad \mathbf{K}_t\Delta\mathbf{d}=\mathbf{f}_{\rm ext}-\mathbf{f}_{\rm int}'],
      6:[r'\sigma_{\rm JC}=(A-B\varepsilon^n)(1+C\ln\dot{\varepsilon}^{*})(1-T^{*m})(G/G_0)^q(1-\phi)^r',
         r'\hat\sigma=\exp\left[\frac{1}{5}\sum_{k=1}^{5}\left(\ln\sigma_{{\rm JC},k}+\delta_k\right)\right]'],
      7:[r'\mathcal{L}=\frac{1}{N}\sum_i\left(\frac{\hat\sigma_i-\sigma_i}{s_y}\right)^2+\lambda\mathcal{L}_{\rm phys}+\frac{\alpha}{N}\sum W^2',
         r'{\rm score}=\frac{1}{2}({\rm RMSE}_{\rm case\ CV}+{\rm RMSE}_{\rm group})'],
      8:[r'g(\Delta p)=q_{\rm trial}-3G\Delta p-\sigma_y(p_n+\Delta p)=0',
         r'\Delta p^{(j+1)}=\Delta p^{(j)}+\frac{g(\Delta p^{(j)})}{3G+H}',
         r'\mathbb{C}_{\rm alg}=\frac{\partial\boldsymbol{\sigma}_{n+1}}{\partial\Delta\boldsymbol{\varepsilon}}'],
      9:[r'W_A\approx h\int\sigma\,d\varepsilon_{\rm inelastic}'],
      10:[r'\frac{d\sigma}{d\phi}=-2700\frac{\partial\sigma}{\partial\rho}-25300\frac{\partial\sigma}{\partial G}',
          r'K_I=Y\sigma\sqrt{\pi a},\qquad a_c=\frac{K_{IC}^2}{\pi Y^2\sigma^2}\quad (Y\ {\rm constant})'],
      12:[r'\mathcal{D}=\boldsymbol{\sigma}:\dot{\boldsymbol{\varepsilon}}-\dot\psi\geq0,\qquad E_t=\frac{EH}{E+H}']}
    lessons=resolve((SOURCE/'study-handbook.md').read_text(encoding='utf-8'))
    objectives = [
        'Distinguish the material predictor, constitutive wrapper and structural solver. Separate numerical verification from physical validation.',
        'Connect processing, microstructure, strengthening and pores. Explain why scalar density cannot identify a dangerous flaw.',
        'Derive von Mises stress, elastic modulus relationships and the J2 flow rule. Distinguish total from plastic strain.',
        'Derive the weak form, element internal force and global Newton equation. Explain interpolation, quadrature and boundary idealisations.',
        'State the actual solver, elements, imposed displacement and material conditions. Explain the two different four-percent study points.',
        'Explain every backbone factor, prove the shape limitation, count network parameters and derive the geometric ensemble.',
        'Distinguish training, selection and testing. Interpret lambda = 0, the control result, metrics and identifiability.',
        'Derive the local consistency residual and Newton denominator. Explain the tangent, range flags and fixed-rate approximation.',
        'Explain localisation, mesh-dependent dissipation and misleading endpoint agreement. Identify the evidence needed for regularisation.',
        'Differentiate along the assumed G(phi) relation. Derive the conditional flaw-size expression and explain why no project CL is reported.',
        'State a defensible conclusion with evidence and limitations. Avoid converting a numerical peak into a strength claim.',
        'Challenge thermodynamic admissibility, strain measures, homogenisation and loading-path transfer. Identify unmodelled physics.'
    ]
    for n, content in enumerate(re.split(r'^## \d+\. ',lessons,flags=re.M)[1:],1):
        title, text=content.split('\n',1)
        story += [PageBreak(),para('PART I / THE CONNECTED THEORY',kicker),para(f'{n}. {title}',chapter)]
        story += [box('LEARNING OBJECTIVES', objectives[n-1]),Spacer(1,5*mm)]
        for tex in equations.get(n,[]):
            equation(tex)
        for block in text.strip().split('\n\n'):
            story.append(para(block[4:],section) if block.startswith('### ') else para(block))
        if n==6:
            figure('figures/fig_architecture.png','Figure 1. Saved JC-PINN architecture. Source: figures/fig_architecture.png.')
        if n==9:
            figure('figures/fig_mesh.png','Figure 2. Saved bracket mesh study. A converged elastic slope does not establish a converged post-yield response. Source: figures/fig_mesh.png.')

    for number,name,part in [(13,'viva-bank','PART II / ADVANCED ORAL DEFENCE'),
                              (14,'team-workbook','PART III / EXAMINATION AND TEAM PRACTICE')]:
        content=resolve((SOURCE/f'{name}.md').read_text(encoding='utf-8'))
        title,content=content.split('\n',1)
        story += [PageBreak(),para(part,kicker),para(f'{number}. {title.lstrip("# ")}',chapter)]
        for block in content.strip().split('\n\n'):
            if block.startswith('## '):
                story.append(para(block[3:],section))
            elif block.startswith('### '):
                story.append(para(block[4:],ParagraphStyle('Question',parent=section,fontSize=11,leading=16)))
            elif block.startswith('Follow-up:'):
                story.append(para(block,ParagraphStyle('Followup',parent=body,fontName='TextItalic')))
            else:
                story.append(para(block))
    story += [PageBreak(),para('Evidence and further reading',chapter)]
    index=(SOURCE/'README.md').read_text(encoding='utf-8')
    # Include project authority and references, without confusing build instructions with lessons.
    for block in index.split('## Authority and reading conflicts',1)[1].split('\n\n'):
        block=block.strip()
        if block.startswith('## '): story.append(para(block[3:],section))
        elif block: story.append(para(block))
    def furniture(canvas,doc):
        if doc.page==1: return
        canvas.saveState()
        canvas.setStrokeColor(INK)
        canvas.line(27*mm,280*mm,183*mm,280*mm)
        canvas.setFont('Head',8)
        canvas.drawString(27*mm,284*mm,'TEAM 8 | MATERIALS, FINITE ELEMENTS AND JC-PINN')
        canvas.drawString(27*mm,15*mm,'Study edition | 17 November 2026')
        canvas.drawRightString(183*mm,15*mm,str(doc.page))
        canvas.restoreState()
    out=PDF/'project-textbook.pdf'
    doc=Book(str(out),pagesize=(210*mm,297*mm),title='Materials, Finite Elements and Neural Constitutive Modelling',author='Team 8')
    doc.addPageTemplates(PageTemplate(id='book',frames=[Frame(27*mm,24*mm,WIDTH,250*mm,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=furniture))
    doc.multiBuild(story)
    print(f'Published {out.relative_to(ROOT)} with {equation_no} numbered equations.')


if __name__=='__main__':
    main()
