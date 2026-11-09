# Course report and shared LaTeX sources

| File | What it is |
|---|---|
| `report.pdf` / `report.tex` | Course report on the final JC-PINN model (14 pages). |
| `numbers.tex` | Every number quoted in the report, paper and slides, generated from `reports/jc_pinn_20261107/` by `scripts/write_latex_numbers.py`. Do not edit by hand. |
| `numbers.json` | The same values, for the slide builder. |
| `refs.bib` | Bibliography shared with `paper/paper.tex`. Every entry was checked against its DOI, publisher page or arXiv record. |

The IEEE-format paper is in [`../paper/`](../paper/paper.pdf). Figures come from [`../figures/`](../figures), written by `scripts/make_figures.py`.

## Rebuild

```bash
python scripts/make_figures.py
python scripts/write_latex_numbers.py
cd report && latexmk -pdf report.tex && cd ../paper && latexmk -pdf paper.tex
```

To get LaTeX on Debian or Ubuntu, install `texlive-latex-extra`, `texlive-publishers` (for IEEEtran), `texlive-science` and `latexmk`.
