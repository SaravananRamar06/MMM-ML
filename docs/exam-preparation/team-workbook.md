# Exam, blackboard and presentation workbook

Suggested preparation times and marks are practice choices, not the university's announced exam format. Use the existing 24-slide corrected deck (`presentation/Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx`); this guide adds teaching and rehearsal without changing the submitted deck.

## 1. Worked calculations: show every unit

### A. Porosity, modulus and the two 4% cases

At phi=0.04, rho=2700*(1-0.04)=2592 kg/m^3. At the original fixed-G study point, E=2*24541*(1+0.33)=65279.06 MPa. Under D5 at the same phi, G=25300*0.96=24288 MPa and E=2*24288*1.33=64606.08 MPa. The density is identical; the modulus assumption differs. Explain this before comparing bracket results.

### B. Dimensionless temperature and rate

At 100 degrees C, Tstar=(100-30)/(600-30)=0.122807. At rate 1e-4 s^-1, rate/rate0=10 and ln(10)=2.302585. The neural feature log10(rate) is -4. At 200 degrees C, Tstar=170/570=0.298246. These normalisations do not validate the model up to 600 degrees C.

### C. Stress invariants

For principal stresses (120,60,0) MPa, sigma_m=60 MPa and s=(60,0,-60) MPa. sigma_eq=sqrt[(3/2)*(3600+0+3600)]=103.923 MPa. Adding 50 MPa to each principal stress changes the mean to 110 MPa but leaves sigma_eq unchanged. For pure shear tau=50 MPa, sigma_eq=86.603 MPa. A material yielding at 136 MPa uniaxially would yield in pure shear near 136/sqrt(3)=78.52 MPa under ideal J2 assumptions.

### D. One linear-hardening radial-return step (teaching example)

These numbers are invented for algebra practice, not a new project result: q_trial=160 MPa, G=25000 MPa, sigma_y(p_n)=140 MPa and constant H=1000 MPa. Consistency gives Delta p=(160-140)/(3*25000+1000)=0.000263158. Then q_new=160-75000*Delta p=140.263158 MPa, equal to 140+1000*Delta p. The equality is the yield-consistency check. With H=-1000 MPa, Delta p=20/74000=0.000270270 and q_new=139.729730 MPa; the local denominator is positive even though the law softens. This does not establish spatial stability.

### E. Neural parameter count and ensemble

First layer: 80 weights plus 16 biases=96. Second: 256+16=272. Output:16+1=17. Total=385. Add seven equation parameters per member:392. Five members:1960. For two illustrative member stresses 100 and 144 MPa, geometric mean=sqrt(14400)=120 MPa; arithmetic mean=122 MPa. For identical member predictions both means agree.

### F. Do not confuse mean curve RMSE and pooled RMSE

Illustrative equal-length curves with RMSEs 1 and 3 MPa give mean curve RMSE=(1+3)/2=2 MPa. The pooled RMSE=sqrt((1^2+3^2)/2)=sqrt(5)=2.236 MPa. In general the square-root operation does not commute with averaging. Our headline metric averages the per-curve roots.

### G. Balanced selection score and rounding

Using displayed values, 0.5*({{SelCV}}+{{SelGroups}})=4.1665 MPa, close to the saved displayed score {{SelScore}} MPa. Rounded inputs need not reconstruct a rounded output exactly. Use the underlying saved values for exact comparisons and never alter a result to force displayed arithmetic agreement.

### H. Mesh effect

Using rounded peaks, (175.6-190.4)/190.4*100=-7.77%. The authoritative saved result is {{BrMeshPeakChangePct}}% because it uses unrounded values. Element count grows by (5/2.5)^3=8, giving 7304*8=58432. This geometric count does not imply a known convergence order for the softening solution.

### I. Partial versus coupled porosity sensitivity

D5 gives d rho/d phi=-2700 kg/m^3 and dG/dphi=-25300 MPa per unit porosity fraction. At fixed T, rate and strain, d sigma/dphi=-2700*(partial sigma/partial rho)-25300*(partial sigma/partial G). Density-only comparisons omit the second term. A percentage-point change of porosity is 0.01 in phi; it is not automatically a 1% relative change in phi or G.

### J. Mesh-objectivity energy argument

Take an illustrative finite inelastic work density of 10 MPa=10 MJ/m^3. A 5 mm band gives 0.005*10 MJ/m^3=50 kJ/m^2; a 2.5 mm band gives 25 kJ/m^2. Using the same strain law halves the represented energy per area. This is a teaching example; no fracture energy has been measured in this project.

### K. Critical flaw length: symbolic exercise only

For constant Y, from K_IC=Y*sigma*sqrt(pi*a_c), square and rearrange to get a_c=K_IC^2/(pi*Y^2*sigma^2). If stress doubles with all assumptions and Y unchanged, a_c falls by a factor of four. When Y depends on a, solve the geometry-dependent equation instead. Toughness in MPa*sqrt(m) and stress in MPa yield a in metres. No project-specific numerical flaw length can be filled in without justified geometry, service stress, toughness and validity checks.

## 2. A demanding 90-minute mock exam (100 marks)

Attempt closed-book first. Write assumptions beside each derivation. Equations with no explanation earn only partial credit.

Question 1 (15 marks, 12 minutes): Explain the process-structure-property chain for LPBF AlSi10Mg. Contrast matrix plasticity, porosity and fracture. Identify which parts our project measures, assumes or omits.

Question 2 (15 marks, 13 minutes): Starting with local equilibrium, derive the weak form and element internal force. Explain the role of B, quadrature, displacement constraints, reactions and the material tangent.

Question 3 (20 marks, 18 minutes): Derive the J2 radial-return residual, its Newton derivative and plastic incompressibility. Explain consistent tangent verification and why local convergence does not establish spatial stability.

Question 4 (20 marks, 17 minutes): Explain the five factors in Equation 1, prove the strain positivity bound and separability limitation, derive the parameter count and geometric ensemble, and interpret lambda=0 and the no-equation control.

Question 5 (15 marks, 15 minutes): Given converged elastic stiffness, a 7.7% peak change, rising EQPS and final-force agreement, assess mesh convergence. Explain the energy argument and propose a regularisation strategy and its missing physical inputs.

Question 6 (15 marks, 15 minutes): Derive the D5 total porosity derivative and critical flaw expression. Explain why the porosity study cannot establish certified strength, fatigue life or critical flaw length. Include at least five limitations specific to our project.

## 3. Marking guide: use after your attempt

Q1: 5 marks for a physically connected processing/microstructure discussion, 4 for strengthening and pores, 3 for separating fracture from yield, 3 for admitting absence of microstructural/experimental characterisation. Invented microscopy or a universal property claim loses the corresponding evidence marks.

Q2: 4 for correct equilibrium and boundary conditions, 4 for integration by parts/virtual work, 3 for N/B/internal force, 2 for constraints/reactions, 2 for quadrature/tangent interpretation.

Q3: 4 for deviator and von Mises definitions, 4 for associated flow and dp=dgamma, 5 for q_new and the residual/derivative, 4 for consistent tangent and a proper finite-difference test, 3 for local/global/spatial distinction.

Q4: 4 for factors and units, 3 for positivity, 3 for separability proof, 3 for 385/1960 and geometric mean, 4 for selected lambda=0 and precise PINN description, 3 for control interpretation and identifiability.

Q5: 4 for rejecting endpoint-only convergence, 4 for the h*work-density argument, 3 for separating boundary concentration and softening, 4 for a justified future regularisation and its calibration needs. Merely saying "use a finer mesh" does not solve the constitutive issue.

Q6: 4 for chain rule under D5, 4 for LEFM derivation and definitions, 3 for small-scale yielding and proper crack-driving stress, 4 for specific missing evidence. Accept units/provenance, test exposure, strain mapping, rate treatment, mesh dependence, assumed nu/G(phi), missing toughness and lack of validation.

## 4. Presenting the corrected 24-slide deck in 15 minutes

The four speaking roles below are suggested responsibilities for rehearsal, not claims about individual contributions. Every member must understand the full chain. Assign names as a team; do not invent who did which implementation.

Speaker A owns motivation, materials and mechanics (slides 1-5, 3 minutes). Speaker B owns architecture, training and selection (6-8, 2.5 minutes). Speaker C owns metrics, control and material sensitivities (9-15, 4 minutes). Speaker D owns FE integration, bracket, mesh and conclusions (16-21, 5.5 minutes). If the team has a different size, merge or split these blocks. Keep at least one backup speaker for each block.

Slide 1, JC-PINN (20 s): "We model the supplied AlSi10Mg stress histories with an equation backbone and learned correction, then transfer the locked model into ANSYS. We assess prediction and numerical behaviour separately."

Slide 2, Can Equation 1 govern an ML material model? (35 s): State the material-surrogate question, 73 supplied cases and 36/37 case split. Say the final lock preceded formal test scoring, while earlier test exposure is disclosed.

Slide 3, Every curve softens (45 s): Read axes before interpreting curves. Explain temperature/rate coverage and missing 300-degree data. Separate observed curve shape from unknown physical cause. Mention the alloy/process background orally without inventing heat treatment.

Slide 4, Equation 1 (45 s): Walk through the five factors and the minus sign. Define Tstar, rate ratio and phi. Be ready to prove positivity and state the units.

Slide 5, Equation 1 cannot bend its curves (35 s): Explain cancellation of non-strain factors in a stress ratio. Handoff: "That shape limitation motivates the correction network."

Slide 6, Model (55 s): Explain delta, exponentiation, zero initial output layer and geometric ensemble. State that five inputs include strain; the network is evaluated along the curve, not emitting all 120 points at once.

Slide 7, Training (45 s): Describe normalised stress loss, regularisation and tested physics residuals. Say immediately that the selected physics weight is zero. Avoid implying collocation enforces a constraint in the submitted fit.

Slide 8, Selection (50 s): Explain case folds, whole-group holdouts and the balanced score. Scalers/constants are refitted inside folds. Handoff: "With this setting fixed, we can now report the formal test."

Slide 9, Test result (40 s): Quote {{TestMean}} MPa mean curve RMSE and {{TestRsq}} R^2. Define the metric instead of reciting only digits.

Slide 10, Bias and spread (30 s): Distinguish signed bias from absolute error and seed spread from calibrated uncertainty.

Slide 11, Alternatives (40 s): Admit the earlier MLPs fit the random test better. Explain why random-split and unseen-group scores answer different questions; old ensemble folds differ.

Slide 12, Control (45 s): "The same-network no-equation control scores better. We therefore claim equation structure and interpretability, not demonstrated accuracy improvement from the backbone."

Slide 13, Improvement screen (20 s): Describe it as post-hoc, training-only exploration. No test-based reselection or retraining for this preparation.

Slide 14, Four-percent study (25 s): Define rho=2592 and original G=24541. Label any above-200-degree curve unvalidated. The later coupled-G case differs.

Slide 15, Porosity (40 s): Explain density-only sensitivity, the small observed effect and why r=0 does not mean no effect. Handoff: "For a structure we also need a multiaxial update and equilibrium."

Slide 16, Finite-element material (65 s): Separate scalar predictor from J2 wrapper. State strain mapping, radial return, consistent tangent, fixed rate and held endpoints. Distinguish offline and single-element verification from validation.

Slide 17, Bracket (65 s): State small strain, prescribed -2 mm displacement and study conditions. Quote {{BrUsermatPeakkN}} kN as a numerical reaction peak. Explain different E in the Workbench comparison and avoid calling it strength.

Slide 18, G coupled to porosity (45 s): State D5 as an assumed upper stiffness bound. At 4%, G=24288. Explain why the coupled effect differs from density-only, and why a stiffness bound is not a formal bound on nonlinear strength loss.

Slide 19, Mesh dependence (70 s): Read the coarse/fine curves and point out peak change, growing strain and misleading endpoint agreement. Explain localisation and absent length scale. State that the hardening comparison supports the softening diagnosis.

Slide 20, Limits (45 s): Prioritise test exposure, simulation-only validation, provenance, total/plastic mapping, prescribed rate, assumed nu/G(phi), extrapolation and mesh dependence. No CL or certified load claim.

Slide 21, Conclusion (40 s): "We delivered a reproducible locked material surrogate and verified its ANSYS implementation. The control and mesh studies define the limits. Experimental calibration and regularised softening are needed before strength or fracture assessment."

The timings sum to 15 minutes. For an 8-minute slot, prioritise slides 1-6, 8-9, 12, 16-21 and compress background/comparisons; retain the control and mesh limitations. Do not silently hide unfavourable evidence. For a longer slot, use the blackboard derivations and take questions rather than reading more text from slides.

## 5. Blackboard practice and cross-examination

Each person should perform these without notes: draw the full modelling chain; derive weak equilibrium; derive von Mises pure-shear yield; derive E from G and nu; derive the J2 consistency residual; prove Equation 1 separability; count parameters and state the ensemble; derive the D5 chain rule; explain band-energy scaling; derive a_c and reject unjustified substitution of project numbers.

Use a three-person rotation: candidate, examiner and evidence checker. Examiner asks one main question and two follow-ups. Candidate has 20 seconds for the direct answer, 60 seconds for supporting derivation/evidence and 20 seconds for limitations. Evidence checker names the relevant saved file and records any unsupported claim. Rotate roles after three questions.

Score each response 0-2 for conceptual correctness, derivation, evidence, assumptions and clear delivery (10 total). For rehearsal only, aim for at least 8/10 twice, with no zero in correctness or assumptions. This is a team readiness target, not an institutional grade prediction.

When you do not know: "That was not identified in our data. Our implementation assumes X; establishing Y would require Z." Do not use uncertainty to avoid answering basic theory. Derive what you can, then delimit the evidence.

## 6. Three-day preparation plan

Day 1 (about 3 hours): Everyone reads handbook sections 1-5, draws the mechanics chain and solves worked examples A-D. Then study sections 6-8 together and each derive the parameter count and local return residual. End with a 20-minute closed-book explanation by randomly selected members.

Day 2 (about 3 hours): Study mesh, porosity and fracture. Run the 90-minute mock exam individually, then mark using the guide. Review errors as a team. Practise viva chains C-E, especially the strain mapping, local/global convergence and lack of strength validation.

Day 3 (about 2.5 hours): Two timed full rehearsals with slide handoffs. Between them hold a 30-minute hostile-but-constructive viva: choose the control, lambda=0, mesh dependence, E mismatch and CL omissions. Check that every member can answer outside their speaking block. End with a 15-minute facts-and-units round and prepare offline backups.

If only one evening remains: spend 30 minutes on the complete chain, 45 on the J2/model derivations, 30 on control/mesh/limits, 30 on the timed deck and 30 on cross-questioning. This prioritises understanding under pressure; it cannot substitute for a full mechanics course.

## 7. On the day

Keep the deck PDF and PPTX, these printable guides, the saved figures and a short evidence index available offline. Use existing saved predictions for any demonstration; the submitted model is locked. Do not retrain or tune during exam preparation. Agree on who takes questions first and how others add corrections briefly. Each member should state their actual contribution and be able to explain the full model-to-bracket pipeline.
