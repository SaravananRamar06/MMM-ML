# Open questions

Last updated: **2026-10-31**. Ask questions when their answers affect the next step; avoid repeatedly asking the user for facts they have already said they do not know.

**Resolved target definition: CL = critical flaw length (confirmed 27 October 2026). It is not coefficient of lift. Do not ask again.**

**Selected working assumption, 31 October 2026:** the user chose fixed nominal
porosity of 4% (`phi = 0.04`) for the planned study. This resolves the nominal
value to use as an assumption, not Q03's physical density/G interpretation or
the porosity of each supplied history. Applicability of the existing curves
to that study condition remains unverified.

**File availability resolved, 31 October:** the user has supplied all files
they have; there are no additional VPSC inputs or run logs. Q01's generating
law remains scientifically unresolved. Investigate a literature-grounded
constitutive hypothesis and qualify it before the requested MLP/PINN build;
do not repeatedly ask the user for missing source files.

## Scientific questions to resolve through evidence

| ID | Question | Why it matters | Best next evidence |
| --- | --- | --- | --- |
| Q01 | What solver, physical model, and loading protocol generated the material histories? | Determines scale, history dependence, target interpretation, and valid constraints. | Professor's original message/input files; otherwise document inference limits. |
| Q02 | What do `Evm`, `Svm`, component strains, and time mean, and what are their units? | Prevents training against incorrectly interpreted quantities. | Documentation plus numerical consistency checks. |
| Q03 | Why do density and shear modulus vary independently? Are either intended to represent porosity? | Controls whether porosity labels can be derived at all. | Professor/input definition. The lower levels are exactly 0.97 and 0.9215 of 2700 and 25300 (implying φ = 0, 3, 7.85 %), but the matrix crosses ρ and G independently, so ratios alone are insufficient. |
| Q04 | What flaw geometry and fracture model define the intended CL task: surface or embedded flaw, LEFM or elastic-plastic (J-integral)? | The name is confirmed; the calculation is not specified. | Professor notebook or original brief. |
| Q05 | What fracture toughness K_IC should be used for the LPBF AlSi10Mg bracket? | The material files contain no toughness data, and a_c scales with K_IC². | Professor, a measured value, or literature (about 20–30 MPa√m reported for LPBF AlSi10Mg). |
| Q06 | How is porosity supposed to affect CL in this project: through flow stress, net-section loss, pores acting as flaws, or reduced toughness? | No connection is established by the supplied histories, and the old fracture deck's numbers are unverified. | Professor's intended workflow and applicable physics. |
| Q07 | What explains initial nonzero stresses and the lower final stress observed in all 73 histories? | Determines physical interpretation and valid loss constraints; the numerical observation is established, its cause is not. | Generating-model information, supported by the saved all-file audit. |
| Q08 | How will material predictions be transferred to the bracket? | Needed for an evidenced multiscale claim. | Defined effective properties and teammate's actual ANSYS setup. |

## Context to obtain when available

- Exact final deadline and submission format.
- Confirm whether "at most two models" is an explicit requirement and what counts as a model.
- Any professor feedback on the submitted presentation.
- Which ANSYS systems actually solved and what files/results are available.
- Whether "only ANSYS results submitted" referred to a separate assessment or to the PDF.

## Resolved in conversation

- Dataset source/material: professor-supplied AlSi10Mg; independent of the part.
- Dataset completeness: complete as supplied, although 35 matrix outputs are absent.
- Split unit/method: random half of cases for training, half for testing.
- Intended capabilities: material stress–strain prediction and porosity-to-CL functionality; CL is critical flaw length (confirmed 27 October 2026).
- Coefficient-of-lift interpretation: withdrawn by the user on 27 October 2026.
- Presentation origin: generated using Claude; the professor dataset was not provided to it.
- User execution of old code: none downloaded or run. Later-inspected handoff contains embedded excerpts.
- Professor's approval: topic only, not the presentation's specific methodology.
- First-principles phrase: user preference, not professor requirement.
- User skill level: good Python, new to ML; wants conceptual preparation for the viva.


## 31 October effective-equation follow-up

Effective-law scope and 36/37 split are user-confirmed. Both tested families/maps fail qualification; see effective-equation-check.md. Open: supported condition/state dependence, case-60 loading/numerical interpretation, physical stress units and original constitutive definitions. User confirms all available files are supplied; do not re-request original inputs.
