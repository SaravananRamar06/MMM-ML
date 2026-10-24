# Project context questionnaire

Prepared 24 October 2026. This collects the remaining context for the AlSi10Mg course project in one place. It is a questionnaire, not a list of facts we have established.

## How to answer

- Start with **Q01–Q12**; these have the largest effect on project direction. All other questions are available now so you can answer in one pass if you prefer.
- Write below each **Answer:** line, or reply in chat using the question IDs. Short answers are fine.
- `Unknown — ask professor`, `Unknown — ask teammate`, `Not applicable`, and `Decide for me` are valid answers. You do not need to invent technical explanations or make ML design decisions yourself.
- If a section does not apply, mark the whole section not applicable. The aerodynamic questions are conditional on the actual CL deliverable; ANSYS specifics can be answered by its owner.
- Add the source when available: professor's words, a file path, a message, a result export, or your own preference. Distinguish a requirement from your current guess.
- These are all the questions we can identify now. Your answers or new files may reveal follow-ups; this cannot guarantee that no further scientific questions will arise.
- Codex/Claude may add evidence-backed notes separately. Neither should fill your answers by inference. User answers become confirmed context only after they are actually provided.

## Already known — correct only if necessary

| Topic | Current confirmed context |
| --- | --- |
| Course/material | Multiscale Modelling of Materials using Machine Learning; professor identified AlSi10Mg. |
| Roles | Four people; you handle ML and another teammate handles ANSYS. You report the other two have not contributed so far. |
| Skills | You know Python, are new to ML, and want to understand/defend concepts while using AI-assisted implementation. |
| Data | Professor supplied material data independent of the bracket geometry; folder is complete as received. |
| Split | Professor requested random 50/50 selection of simulation cases. |
| Model count | You recall at most two neural-network models; exact scope of that limit is uncertain. |
| CL | **Coefficient of lift**, explicitly confirmed. Do not reinterpret it as critical flaw length. |
| Intended functionality | Both material-response prediction and porosity-to-CL functionality have been discussed; their required connection remains unresolved. |
| First principles | Your suggestion, not an established professor requirement. |
| Existing submission | The local PDF was actually submitted; generated with Claude without the professor's dataset. You did not download/run its prior analysis code. |
| Approval | Professor approved the topic, not the specific equations or numerical claims in the PDF. |
| Deadline | Next month relative to 24 October 2026; exact date pending. |
| Current work | Codex research/audit complete. Claude has since reported implementation/experiments and created a 36/37 split; independent review pending. |
| Collaboration | You want a shared dashboard/chat with Codex and Claude. Codex adds its own usage panel; Claude will add its panel. |

Numerical observations and the research recommendation are in [research.md](research.md), [dataset.md](dataset.md), and the audit notes. They are not professor instructions.

## A. The 12 questions that matter most

Likely sources: you, the professor's notebook/brief, and your ANSYS teammate.

**Q01. What is the closest verbatim version of the professor's project instruction, including the note about CL versus porosity?** Include any wording you remember even if incomplete; do not reconstruct an equation from the old PPT.

**Answer:**

**Q02. Is predicting stress–strain response explicitly required by the professor, a supporting step towards CL, or a useful model we are proposing ourselves?** Your earlier answer confirmed both intended outputs; this asks which are mandatory versus supporting choices.

**Answer:**

**Q03. What connection did the professor intend between material porosity, the wing/rib bracket, and coefficient of lift?** Describe the expected chain in words, or mark unknown.

**Answer:**

**Q04. What aerodynamic data, calculation, or simulation is supposed to provide CL values?** If none has been supplied or performed, say so explicitly.

**Answer:**

**Q05. What does the professor expect the word “multiscale” to mean in this project?** For example, which smaller-scale quantity is supposed to influence which larger-scale result? The course title alone does not settle this.

**Answer:**

**Q06. Can the professor identify the software, material law, and loading setup that generated `STR_STR.OUT`?** If you do not know, who can obtain that explanation?

**Answer:**

**Q07. Is there any original unit/column description for the material data, and who can confirm it?** We have numerical consistency checks, but not authoritative definitions of every field.

**Answer:**

**Q08. What exactly does “at most two models” count?** Two network architectures, two final trained predictors, a comparison of two approaches, or something else? Is this a firm rule or your recollection?

**Answer:**

**Q09. Did the professor say anything about validation or tuning within the training half, beyond the confirmed random 50/50 case split?** We can choose a standard training-only method if unspecified.

**Answer:**

**Q10. What was actually submitted as ANSYS work, separately from or together with the local PDF whose provenance says Python?** List the submitted files/results and which claims came from actual solver runs.

**Answer:**

**Q11. What are the exact final submission, presentation, and intermediate-review dates?** Include any deadlines for getting teammate results.

**Answer:**

**Q12. What determines the grade?** Give the rubric, expected demonstrations, professor's priorities, or examples of what counts as a successful project.

**Answer:**

## B. Assignment boundaries and expectations

Likely sources: professor/assignment documents. If unspecified, say so; we can make routine implementation choices.

**Q13. Is the approved project title fixed, or may it change to match the actual data and methods once the scope is clarified?**

**Answer:**

**Q14. Are the ML exercise, ANSYS comparison, porosity investigation, and aerodynamic CL task separate assessments or one required connected pipeline?**

**Answer:**

**Q15. Which neural-network types, modelling methods, or physics concepts have been taught and are expected to appear in the explanation?**

**Answer:**

**Q16. Are there restrictions on frameworks or prebuilt libraries, or are ordinary Python/PyTorch/scikit-learn implementations acceptable?**

**Answer:**

**Q17. Are additional simulations, external datasets, or literature parameters allowed, and must any be approved before inclusion?**

**Answer:**

**Q18. Does the professor expect prediction accuracy, physical interpretation, an actual material-to-part demonstration, or some specified balance of these?**

**Answer:**

**Q19. What feedback or questions did the professor give after seeing the submitted presentation?** Include criticism, corrections, and items they said to complete next.

**Answer:**

**Q20. What parts of the scope are we free to simplify if the remaining time or available data cannot support the original plan?**

**Answer:**

## C. Data origin and coverage

Likely source: professor or whoever provided the dataset. No need to know the answers from memory.

**Q21. Where is the original message/download/archive that accompanied `TEAM_8_extracted_results_set_1`?** Give its location and any explanatory wording; no account credentials are needed.

**Answer:**

**Q22. Does “set 1” distinguish it from any other available sets, load paths, microstructures, or future releases?** We know this folder is complete as received; this asks whether other separately named data exists.

**Answer:**

**Q23. Are the histories generated simulations, measurements, processed outputs, or some combination?** The directory names suggest simulations; can the source confirm this?

**Answer:**

**Q24. What material-scale object is simulated: material point, crystal, polycrystal/RVE, test coupon, or another representation?**

**Answer:**

**Q25. Why do 35 matrix cases have no output, including all cases at the 300 temperature level?** Are they unrun, failed, withheld, or intentionally excluded? Treat unknown as unknown, not a download fault.

**Answer:**

**Q26. Are there replicate runs, random seeds, different microstructures/orientations, or relationships between case IDs that the matrix does not record?**

**Answer:**

**Q27. Can any generating input decks, material parameter files, solver logs, or scripts be obtained?** Which person has them?

**Answer:**

**Q28. Has the professor flagged any invalid case, known numerical issue, or deliberate anomaly—particularly case 60?** We will retain it unless there is an evidence-backed reason to treat it differently.

**Answer:**

## D. Column meanings and loading conditions

Likely source: generating code/documentation or professor. These are requests for definitions, not a test of your materials knowledge.

**Q29. What are the units of time, temperature, stress, density, shear modulus, and strain rate?** Is matrix temperature Celsius while output `TEMP` is Kelvin, as the numbers suggest?

**Answer:**

**Q30. What precisely is `E11`—total, elastic, plastic, engineering, logarithmic, or another strain measure?**

**Answer:**

**Q31. How is `Evm` defined and accumulated?** Is its reversal in case 60 expected under that definition or a numerical/processing concern?

**Answer:**

**Q32. Are `SCAUij` and `Svm` material-point values, spatial averages, volume averages, or another output?** The audit checks numerical consistency but cannot establish averaging.

**Answer:**

**Q33. Are the shear strain components tensor shear or engineering shear, and which coordinate system/orientation do the components use?**

**Answer:**

**Q34. What loading mode, lateral constraints, initial state, and rate definition were prescribed?** Are all cases the same loading path apart from the listed conditions?

**Answer:**

**Q35. What explains the nonzero initial stress and lower final stress seen in all 73 cases?** For example, does the output omit an initial stage or describe a particular inelastic mechanism? Do not choose an explanation without evidence.

**Answer:**

**Q36. What ends a run, and are temperature, density, and shear modulus held constant or evolved during it?** Is any damage/failure event explicitly recorded?

**Answer:**

## E. Material state and meaning of porosity

Likely sources: professor, material references, teammate's Engineering Data.

**Q37. What manufacturing route and material condition does the professor's AlSi10Mg data represent?** Is it the same condition as the bracket study?

**Answer:**

**Q38. Are heat treatment, build direction, crystallographic texture, anisotropy, or residual stress specified?** Which are intentionally neglected?

**Answer:**

**Q39. What does the matrix's density variation physically represent?** Is it bulk density, a model parameter, or explicitly a surrogate for porosity?

**Answer:**

**Q40. Why is shear modulus varied independently of density?** Is there a prescribed physical mapping, sensitivity study, or deliberate numerical design?

**Answer:**

**Q41. If density is used to derive porosity, what fully dense reference and equation were specified?** No reference/mapping is confirmed yet.

**Answer:**

**Q42. What porosity range and definition should the final project use—volume fraction, area fraction, relative density, or something else?**

**Answer:**

**Q43. Does “porosity” refer to internal AM defects, intentional structural holes, surface permeability, or another physical feature in the aerodynamic discussion?** This distinction may determine the material-to-CL connection.

**Answer:**

**Q44. Are pore shape, size, clustering, location, or CT/micrograph measurements available or required, or is a scalar porosity intentionally sufficient for the assignment?**

**Answer:**

## F. Aerodynamic CL task

CL is already confirmed as **coefficient of lift**. These questions concern the actual aerodynamic problem, not its acronym. Mark unavailable information explicitly; do not substitute fracture calculations.

**Q45. Which object's lift is of interest: a full wing, an airfoil section, an assembly containing the bracket, or another object?** What aerodynamic geometry is available?

**Answer:**

**Q46. Is a baseline CL value, curve, or aerodynamic model already available?** Where did it come from, and at what conditions?

**Answer:**

**Q47. What flow conditions and reference quantities are prescribed?** List available angle of attack, speed/Mach or Reynolds number, fluid properties, and reference area/length rather than calculating missing values by guesswork.

**Answer:**

**Q48. Is the required target one CL value at a fixed operating condition, a CL-versus-porosity curve, a lift curve over angle of attack, or a multi-condition predictor?**

**Answer:**

**Q49. Does the professor intend material stiffness/deformation to change aerodynamic shape, flow through porous surfaces to affect lift, or some other stated mechanism?** If no mechanism was stated, mark that gap.

**Answer:**

**Q50. Who can run or supply the aerodynamic calculation—CFD, an analytical model, experiments, or existing data—and what software/resources are available?**

**Answer:**

**Q51. If structural deformation is involved, how should geometry changes or loads be transferred between the structural and aerodynamic calculations, and is one-way or iterative coupling expected?** Mark not applicable if this is not the intended mechanism.

**Answer:**

**Q52. What aerodynamic reference or result would validate the final CL prediction?** Are any accuracy targets or comparison requirements prescribed?

**Answer:**

## G. Multiscale connection and project narrative

Likely sources: professor's intended workflow and the team's actual simulations. We can help design a defensible connection once scope is established.

**Q53. What are the named scales in the intended project, and what information is available at each?** Do not assume a pore-scale simulation exists just because the PPT describes one.

**Answer:**

**Q54. Which material quantities should ML supply to a larger-scale model: full stress–strain curves, yield stress, effective modulus, constitutive parameters, or something else?**

**Answer:**

**Q55. Is there a prescribed homogenisation/upscaling method, or can we select one and explain its assumptions?**

**Answer:**

**Q56. Does the assignment require using ML predictions inside ANSYS, or is comparing predictions with simulation results sufficient?**

**Answer:**

**Q57. What demonstrates that information genuinely passes between scales rather than the ML and ANSYS work being separate examples?** Is a particular demonstration expected by the professor?

**Answer:**

**Q58. Are material conditions uniform throughout the bracket/wing, or is a spatially varying material/porosity field expected?**

**Answer:**

**Q59. Is the desired contribution faster prediction, understanding parameter effects, finding a porosity limit, improving a design, or another concrete outcome?**

**Answer:**

**Q60. What practical decision should someone be able to make using the completed model?** Give an example in plain language if possible.

**Answer:**

## H. Actual ANSYS work and integration

Likely owner: the teammate who performed the ANSYS work. One answer can reference a setup/results document instead of retyping every setting.

**Q61. Which exact ANSYS analyses have actually been solved, and which are demonstrations, incomplete setups, or plans?** Include static elastic, static elastoplastic, explicit Johnson–Cook, and any aerodynamic analysis only if actually present.

**Answer:**

**Q62. Where are the current CAD, complete Workbench archive/project, solver files, exported tables, and screenshots?** Which versions correspond to submitted results?

**Answer:**

**Q63. What are the actual geometry units, supports, contacts/pin assumptions, load directions/magnitudes or prescribed displacements, and loading histories for each relevant run?**

**Answer:**

**Q64. Which material model, elastic constants, hardening/failure parameters, temperature, and rate were actually assigned?** Cite the current Engineering Data rather than the old handoff's alternatives.

**Answer:**

**Q65. What mesh/convergence, nonlinear convergence, large-deformation, or explicit quasi-static checks were performed, and which warnings remain?**

**Answer:**

**Q66. Which quantities and units can be exported for comparison or ML coupling—reaction/displacement, stresses, strains, effective stiffness, failure load, or others?**

**Answer:**

**Q67. Has porosity actually been represented in ANSYS?** If yes, how; if not, which assumptions or property changes were merely proposed?

**Answer:**

**Q68. Can the teammate rerun analyses with an ML-derived material curve/property table, and what import format or interface would they need?**

**Answer:**

## I. Prediction contract, evaluation, and model comparison

Likely source: professor's requirements where specified; otherwise we can decide. These are not requests for you to design the optimiser.

**Q69. What should a user enter and receive in the finished material model?** A curve, stress at a chosen strain, derived properties, or multiple outputs? The research proposes a strain-query curve model.

**Answer:**

**Q70. What prediction ranges are actually needed for temperature, rate, density/modulus, porosity, and strain?** Are predictions between existing conditions sufficient or are new regimes required?

**Answer:**

**Q71. Must the material model handle unloading, cyclic loading, multiaxial paths, or other histories absent from the current dataset?** If yes, what additional training evidence will be available?

**Answer:**

**Q72. Does the professor require particular metrics, error tolerances, plots, or separate results for each test case?** If not, we will propose suitable curve-level metrics.

**Answer:**

**Q73. Is prediction of rare/abnormal curves particularly important, and is there a prescribed policy for invalid runs?** We currently retain and flag case 60; no basis for deleting it is established.

**Answer:**

**Q74. Is the second model expected to compare architectures, compare representations, add physics, or predict a different quantity such as CL?** If no expectation exists, we can decide after the first baseline.

**Answer:**

**Q75. Are uncertainty estimates, feature-effect explanations, or sensitivity plots required, optional, or outside the course scope?**

**Answer:**

**Q76. What result would you consider disappointing even if an overall accuracy score looked high?** For example, poor curve shapes, failure on a particular condition, or inability to explain the result.

**Answer:**

## J. Computing environment and development workflow

Likely source: you and Claude. No passwords, API keys, or paid-account tokens are needed.

**Q77. On which computer/environment must the final model run—this Linux workspace, a teammate's Windows laptop, Colab, or another setup?**

**Answer:**

**Q78. What CPU/RAM/GPU resources are available, and are remote/cloud compute or paid services allowed if ever needed?** A small first model may not need a GPU.

**Answer:**

**Q79. Are there installation, internet, storage, offline-demo, or college-lab restrictions we should design around?**

**Answer:**

**Q80. Which environment manager/framework do you prefer, or should we choose and provide one reproducible setup?**

**Answer:**

**Q81. Should the final interaction be a notebook, command-line script, browser form, or a combination?** This refers to model inference; the collaboration dashboard already has its own chat role.

**Answer:**

**Q82. What work has Claude already started, which files is it editing, and what independent findings or decisions has it made that are not yet in our Markdown context?**

**Answer:**

**Q83. Are Claude and Codex using exactly the same project directory, or separate copies/worktrees that need an explicit exchange path?** The local room assumes a shared filesystem.

**Answer:**

**Q84. What backup/version-control arrangement do you want for code, model weights, and documentation?** Is a repository already maintained elsewhere? Local inspection initially found no Git repository here.

**Answer:**

## K. Final report, presentation, demonstration, and viva

Likely source: you and the assignment instructions.

**Q85. What exact files must be submitted: source code, notebook, saved model, dataset, report, slides, ANSYS archive, or demonstration recording?**

**Answer:**

**Q86. What report length, section structure, formatting, citation style, or template is prescribed?**

**Answer:**

**Q87. How long is the presentation, how many slides/speakers are expected, and who answers which technical questions?**

**Answer:**

**Q88. Is there a live demonstration, and must it work offline or on a particular machine?** What time limit and failure fallback are acceptable?

**Answer:**

**Q89. How deep is the viva expected to go into data preparation, neural-network mathematics, material physics, ANSYS settings, and code?** Mention examples from the professor if known.

**Answer:**

**Q90. Which topics currently feel least comfortable to explain?** You can list training/testing, backpropagation, losses, overfitting, material equations, multiscale coupling, or anything else.

**Answer:**

**Q91. Are there required declarations about AI assistance, source attribution, code ownership, or reproducibility in the final submission?** We need the actual course requirements, not assumptions about them.

**Answer:**

**Q92. Which outputs would help you learn and present: annotated plots, a short concept guide, equations with worked examples, practice questions, or a narrated model walkthrough?**

**Answer:**

## L. Team responsibilities, previous work, and success criteria

Likely source: you and teammates. These questions help identify reliable evidence and avoid duplicated work.

**Q93. Who will own the final data clarification, material ML, aerodynamic work, ANSYS integration, report, slides, and demo?** Include unassigned work explicitly.

**Answer:**

**Q94. What useful work can the other two teammates realistically take on now, and when can the ANSYS owner supply their files/results?**

**Answer:**

**Q95. Beyond the current folder, what previous chats, notes, source papers, code archives, or generated artifacts still exist and where?** Distinguish items actually available from items merely claimed in a handoff.

**Answer:**

**Q96. Does anyone have actual raw outputs behind the submitted PPT's plots/scores, and which old results has a teammate independently run or checked?** Embedded code alone is not proof of execution.

**Answer:**

**Q97. Has the professor been told that the submitted CL interpretation was wrong, and is a revised explanation or corrected intermediate submission expected?** We know the target correction; this asks how it affects the assessment history.

**Answer:**

**Q98. How much time can you and the ANSYS teammate spend each week before the final deadline, and are there exams or other constraints?**

**Answer:**

**Q99. If time becomes tight, which outcome should take priority: a rigorous material model, the complete porosity-to-lift chain, reproducible ANSYS integration, or another professor-approved minimum?** We should clarify rather than silently drop a required component.

**Answer:**

**Q100. What important context, concern, professor comment, or disagreement have we still not asked about?** Include anything in Claude's understanding that differs from ours.

**Answer:**

## Answer follow-up record

Leave this for consolidation after answers arrive. It is not permission to guess missing answers.

| Date | Answer IDs incorporated | Facts/decisions changed | Source/evidence | Remaining follow-up |
| --- | --- | --- | --- | --- |

After answers are reviewed, update [context.md](context.md), [decisions.md](decisions.md), [open-questions.md](open-questions.md), and [tasks.md](tasks.md). The questionnaire should preserve the original answer/source when a later clarification changes it.
