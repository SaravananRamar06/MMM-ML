"""Make the 15-content-slide submission deck from the current corrected final deck.

The instructor's limit is 15 content slides plus intro and outro. This script copies
presentation/Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx, keeps the slides
listed in KEEP (cover, 15 content slides, thank-you), drops the rest with their notes, and renumbers
the 'N · ...' kicker of each kept content slide 1..15. Text, numbers and speaker notes are not changed.

Usage: python scripts/make_submission_deck.py [OUTPUT.pptx]
Default output: presentation/submission/Team8_Presentation_source.pptx
"""
import re
import sys
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'presentation' / 'Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx'
# 1-based slide numbers of the 24-slide corrected deck
KEEP = [1,                                                       # cover (intro)
        2, 3, 5, 7, 9, 10, 12, 14, 15, 17, 18, 19, 20, 22, 23,   # 15 content slides
        24]                                                      # thank you (outro)
KICKER = re.compile(r'^(\d+)(\s*·\s*)')


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'presentation/submission/Team8_Presentation_source.pptx'
    prs = Presentation(str(SRC))
    n = len(prs.slides)
    assert n == 24, f'expected the 24-slide corrected deck, found {n}'
    ids = prs.slides._sldIdLst
    entries = list(ids)
    for i, sld in enumerate(entries, 1):
        if i not in KEEP:
            prs.part.drop_rel(sld.rId)
            ids.remove(sld)
    assert len(prs.slides) == len(KEEP) == 17
    content = 0
    for k, slide in enumerate(prs.slides, 1):
        if k in (1, len(prs.slides)):
            continue
        content += 1
        for sh in slide.shapes:
            if sh.has_text_frame and sh.text_frame.paragraphs:
                runs = sh.text_frame.paragraphs[0].runs
                if runs and KICKER.match(runs[0].text):
                    runs[0].text = KICKER.sub(lambda m: f'{content}{m.group(2)}', runs[0].text, count=1)
                    break
    assert content == 15
    # Slide-number fields keep a cached value from the 24-slide deck, and importers (Canva) show that value:
    # set it to the new position. Drop the slide-number placeholder from the notes pages, which some
    # importers append to the speaker notes.
    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    for k, slide in enumerate(prs.slides, 1):
        for t in slide._element.xpath('.//a:fld[@type="slidenum"]/a:t'):
            t.text = str(k)
        if slide.has_notes_slide:
            for sh in list(slide.notes_slide.shapes):
                if sh.is_placeholder and sh.placeholder_format.type is not None and sh.placeholder_format.type == 13:  # SLIDE_NUMBER
                    sh._element.getparent().remove(sh._element)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    print(f'wrote {out} ({len(prs.slides)} slides: 1 intro, {content} content, 1 outro)')


if __name__ == '__main__':
    main()
