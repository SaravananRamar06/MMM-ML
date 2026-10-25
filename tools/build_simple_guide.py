"""Build a readable, printable HTML guide from its editable Markdown source.
Run with .venv/bin/python tools/build_simple_guide.py.
"""
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'project files/My model explained.md'
body = markdown.markdown(source.read_text(), extensions=['tables', 'fenced_code'])
css = '''
:root { color-scheme: light; }
body { margin: 0; color: #263238; background: #f4f5f7; font-family: system-ui, sans-serif; line-height: 1.65; }
main { max-width: 760px; margin: 32px auto; padding: 44px 52px; background: white; }
h1 { font-size: 30px; line-height: 1.2; color: #17394d; margin-top: 0; }
h2 { font-size: 21px; line-height: 1.35; color: #17394d; margin: 34px 0 12px; }
p, li { font-size: 16px; } a { color: #175f8a; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f2f5f7; padding: 16px; font-size: 14px; }
code { font-family: ui-monospace, monospace; font-size: .9em; }
blockquote { margin: 20px 0; padding: 8px 20px; border-left: 3px solid #78909c; background: #f5f8fa; }
table { border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 15px; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #dce3e7; }
th { background: #edf2f5; } img { max-width: 100%; }
@media(max-width: 700px) { main { margin: 0; padding: 24px; } h1 { font-size: 26px; } }
@media print { body { background: white; } main { margin: 0; padding: 0; max-width: none; }
 h2 { break-after: avoid; } p, li { orphans: 3; widows: 3; } pre, blockquote, tr { break-inside: avoid; }
 @page { margin: 19mm; } }
'''
output = source.with_suffix('.html')
output.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>My AlSi10Mg model, explained simply</title><style>' + css + '</style></head><body><main>' + body + '</main></body></html>')
print(output)
