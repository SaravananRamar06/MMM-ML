# Final report factual review

Status: **reference checklist prepared; report draft not yet reviewed**. This checklist does not certify a report that has not been read. Prepared on 25 October 2026 from saved source/model evidence.

## Required numbers and distinctions

| Item | Verified value | Local source |
|---|---|---|
| Planned / available cases | 108 / 73 | Raw matrix; data/manifest.json |
| Raw history rows | 2,197,000 | reports/retests/20261025T172218Z/results.json, source_audit |
| Temperature coverage | 27 at 30, 27 at 100, 19 at 200, none at 300 | data/manifest.json; dataset.md |
| Fixed split | 36 training / 37 test, seed 42 | data/split.json |
| Query grid | 120 E11 values, 0.0002 to 0.0999 | src/data.py |
| Effective training queries | 4,320 from 36 simulations | Fresh source audit; not independent simulations |
| Final model | Five 5–16–16–1 tanh MLPs averaged, linear output | src/models.py; final model artifact |
| Parameters | 385 per network, 1,925 total | Fresh source audit |
| Fit settings | L-BFGS, alpha 0.001, seeds 0–4 | Model artifact; fresh refit |
| Mean / median test curve RMSE | 0.0590851517 / 0.0505666552 | Fresh results, fresh_test_metrics |
| Worst test curve | RMSE 0.1133061791, case 45 | Same |
| Mean curve MAE / pooled RMSE | 0.0489985921 / 0.0648628073 | Same; distinguish pooled from mean curve RMSE |
| Largest test point error | 0.2883202786 | Same |
| Frozen refit | 17.2608 s, no warnings, exact weights/predictions | Fresh results, refit; earlier 25.028 s is a different run |
| Software checks | 13 model/parser/runtime unit tests + 3 live Studio tests | Fresh unit.txt and live_studio_retry.txt |
| Worked example at T100, rate1e-4, density2619, G24541 | 136.20912 at grid start; 99.41858716 interpolated at .05; 75.23194 at grid end | model_numpy.npz; personal guide |

## Saved training-side comparisons

Each row is from `runs/score/select_<candidate>_Svm.json`. CV is mean curve RMSE for the training-side case folds. Condition-holdout is the saved mean over temperature/rate groups; do not label it as a fresh evaluation of the delivered artifact.

| Candidate | Case CV | Condition holdout |
|---|---:|---:|
| Query MLP | 1.15826321 | 6.79360255 |
| PCA + GP (6 components) | 0.66446840 | 10.96182303 |
| MLP/GP blend | 0.86709976 | 7.98303201 |
| Physics-style-input MLP | 1.53568292 | 8.60905759 |
| PCA-coefficient MLP (4 components) | 2.26939310 | 11.08560944 |
| PCA-coefficient MLP (6 components) | 2.00434446 | 11.20549658 |

The query MLP's saved 200 / 1e-5 condition-holdout RMSE is 23.52512868. Case 60 is the sole available case in that condition and lies in the training half. No 300-temperature outputs exist.

## Scientific wording required

- The final target is Svm along operational E11, not SCAU11 and not lift. Units such as MPa, °C and s^-1 remain inferred, not confirmed.
- Earlier full-data exploration occurred. The 37 cases were excluded from final fitting but are not a fully blind holdout.
- Input/output preprocessing for the final fit uses training cases only. All points from one simulation remain in one partition.
- Low random-split error primarily demonstrates interpolation within related simulated conditions. Condition generalisation is substantially weaker.
- Exact reproduction is same-environment numerical reproducibility, not physical, experimental, cross-platform or aerodynamic validation.
- No verified porosity labels, material-to-lift mapping or validated ANSYS coupling exist. C_L means coefficient of lift, never critical flaw length.
- The model is a data-driven surrogate, not a physics-informed loss or verified constitutive law. The histories do not establish a conventional zero-stress elastic loading segment.
- An ANSYS-format export, if provided, is an unvalidated template until units, stress/strain definitions and the receiving material model are confirmed. Do not invent a zero-origin segment or label a total-strain curve as plastic strain.
- Existing presentation files contain 24 image slides with speaker notes. Guides and presentation are deliverables; neither establishes that a formal course report has already passed final review.

## Review result

Awaiting the report source from its owner. Record actual findings and resolved corrections here after reading that source. Rendering/compilation is a separate layout check.

## Draft review — report/report.tex, first source version

Read the complete LaTeX source supplied at 18:29 UTC. All six candidate-table rows, test metrics, parameter counts, split/grid details, worked example and fresh 17.26-second refit agree with the checked artifacts to their displayed precision. The limitations correctly preserve missing units, porosity mapping, lift labels and ANSYS validation. No new fit or model change was needed.

Corrections required before approval:

1. **Figure provenance:** `figures/loco_rmse.png` is an earlier multi-model exploratory plot, with unconditional MPa labelling. `src/evaluate.py` uses default alpha 1e-4, all available cases for condition holdouts and four-component GP; it cannot illustrate the saved training-half alpha0.001 results (mean6.7936, hot/slow23.5251). Replace it with `report/figures/condition_holdout_Svm.png` (or PDF), generated by `reports/plot_report_diagnostics.py` directly from `runs/score/select_mlp_Svm.json`. This is a new plot of saved diagnostics, not a fresh condition-model evaluation.
2. **Interpolation reliability:** abstract/discussion/conclusion describe the model as reliable/accurate throughout sampled input ranges. Change to close reproduction of the 37 related test curves, with reliability at other combinations unestablished even inside the numerical bounds. The sparse groups and irregular case60 prevent a blanket range-wide reliability claim.
3. **Test bias:** replace “the test score is optimistic relative to a fully blind holdout” with “the score is not a fully independent generalisation estimate and may be optimistic.” Its direction/magnitude relative to an unavailable blind dataset is not measured.
4. **Unmeasured improvement:** replace “More simulations ... would help more than a larger model” with a proposed priority for adding data at sparse/missing conditions. No new-data-versus-model-size experiment establishes that comparison.
5. **Test figure caption:** the fresh test_curves.png contains cases42 and45, with lower residual panels; case45 is the worst of37. State that scope rather than implying a plot of all37 cases.
6. **Formal reporting:** add a references/bibliography section for the implemented methods/software and any literature statements actually used, and distinguish the unpublished professor-supplied data source. The current draft has no citations or bibliography.

Status: **numeric values checked; the above scientific/figure/documentation corrections remain open**. Compilation and PDF layout are a separate review.

Additional aggregation wording: the condition-holdout column is the unweighted mean of **nine group-mean curve RMSEs**, not a pooled RMSE or a case-weighted mean across every held-out prediction. State this in the candidate table caption and condition figure discussion; case-CV is the mean over its 36 case errors. Sparse groups have different case counts.

## Second source review

Source SHA-256 before the final aggregation-caption correction: `b05c4b15bfdb16bd9157367aeae808b4823522be2f4d5fb54d60ccd21f883cf0`.

All six listed corrections are present: correct saved-diagnostic figure/provenance, restrained reliability language, qualified possible test bias, data-collection priority stated as a proposal, cases42/45 residual caption, unpublished-data provenance and a bibliography. The remaining item is to state the group-unweighted condition-error aggregation explicitly.

Bibliographic metadata was checked against primary sources:

- Pedregosa et al., JMLR12, 2825–2830 (2011): https://jmlr.org/papers/v12/pedregosa11a.html
- Liu and Nocedal, Mathematical Programming45, 503–528 (1989): https://link.springer.com/article/10.1007/BF01589116
- Rasmussen and Williams, MIT Press (2006): https://gaussianprocess.org/gpml/
- Harris et al., Nature585, 357–362 (2020): https://numpy.org/citing-numpy/
- Hunter, Computing in Science & Engineering9(3), 90–95 (2007): https://matplotlib.org/stable/project/citing.html

These sources support method/software citation metadata, not physical validation of this project.

## Source approval after corrections

Final checked source: `report/report.tex`, SHA-256 `76bc9f93d5ef6963fe652c72b97868aa8a2a71c3c24d935e77c2efd562f3212c`.

Confirmed the final caption defines case-CV over 36 cases and condition holdout as the unweighted mean of nine group means. The results paragraph makes the same distinction. Correct figure search paths are in place. All numerical, provenance and scientific-wording findings from this review are resolved for this source version. **Source factual review: passed.** Compilation, visual layout and final exported-PDF identity remain the document owner's checks; source approval alone does not certify a different later revision or the rendered file.


## Final compiled PDF and layout check

Compiled with verified portable Tectonic0.17.0. Corrected only evidence-block line wrapping and caption alignment after source factual approval; no numerical/scientific claims changed. Final source SHA256: `2b8df5fb67d8b28ddd65ef943908f0b52463f81b6f2e743158877dfc6699e5be`. Final PDF SHA256: `45a1c9f6a71ea6b6a0d5d0b59ffb42fc8c310ca66e3aae1a7624025c45b0fc94`.

All five final pages were rendered and visually inspected. No clipping, overlap, broken tables/references or out-of-page links remain. The final TeX log contains no warnings or overfull/underfull boxes. Text extraction retains the checked metrics, uncertainty wording, references and evidence paths. `project files/Final Course Report.pdf` and `project files/report.pdf` are byte-identical to `report/report.pdf`. The PDF is an actual LaTeX/xdvipdfmx output, replacing the earlier Chromium fallback exports. Build identity is recorded in `report/build_verification.json`.
