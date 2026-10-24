# Open questions

Last updated: **2026-10-24**. Ask questions when their answers affect the next step; avoid repeatedly asking the user for facts they have already said they do not know.

**Resolved target definition: CL = coefficient of lift. Do not ask again whether it means critical length.**

## Scientific questions to resolve through evidence

| ID | Question | Why it matters | Best next evidence |
| --- | --- | --- | --- |
| Q01 | What solver, physical model, and loading protocol generated the material histories? | Determines scale, history dependence, target interpretation, and valid constraints. | Professor's original message/input files; otherwise document inference limits. |
| Q02 | What do `Evm`, `Svm`, component strains, and time mean, and what are their units? | Prevents training against incorrectly interpreted quantities. | Documentation plus numerical consistency checks. |
| Q03 | Why do density and shear modulus vary independently? Are either intended to represent porosity? | Controls whether porosity labels can be derived at all. | Professor/input definition; numeric ratios alone are insufficient. |
| Q04 | What aerodynamic setup, geometry, operating conditions, and reference quantities define the intended C_L task? | The name is confirmed; the actual prediction problem is not specified. | Professor notebook or original brief. |
| Q05 | Where will lift-coefficient labels come from? | Current material files contain no such labels. | Separate aerodynamic dataset, documented simulations, or measurements. |
| Q06 | How is porosity/material response supposed to affect C_L in this project? | No connection is established by the supplied material histories or old fracture deck. | Professor's intended workflow and applicable physics. |
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
- Intended capabilities: material stress–strain prediction and porosity-to-C_L functionality; the user explicitly clarified C_L is coefficient of lift.
- Critical-flaw-length interpretation: superseded and incorrect for the current project target.
- Presentation origin: generated using Claude; the professor dataset was not provided to it.
- User execution of old code: none downloaded or run. Later-inspected handoff contains embedded excerpts.
- Professor's approval: topic only, not the presentation's specific methodology.
- First-principles phrase: user preference, not professor requirement.
- User skill level: good Python, new to ML; wants conceptual preparation for the viva.
