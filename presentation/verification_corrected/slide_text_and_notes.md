<!-- Slide number: 1 -->
MULTISCALE MODELLING OF MATERIALS USING MACHINE LEARNING  ·  COURSE PROJECT
Effect of Porosity on an Additively Manufactured Aircraft Wing Bracket
From AlSi10Mg material data to bracket stress, with a JC-backbone neural network (JC-PINN) and Ansys
TEAM
Pranav Parasuram C   ME24B1061
R Saravanan   ME24I1006
Dinesh Y   ME24B1043
Amit Narayan K   ME24I1024
Course instructor  Prof. Arul Kumar Mariyappan
Indian Institute of Information Technology, Design and Manufacturing (IIITDM) Kancheepuram

### Notes:
Good morning. We are presenting our course project on how porosity from 3D printing affects an aluminium aircraft wing bracket: a neural material model built on a Johnson-Cook backbone, which we call the JC-PINN, the team's Ansys bracket runs, and the fracture step we still plan to add.

<!-- Slide number: 2 -->
01 · PROBLEM STATEMENT
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Printed brackets are light, but they carry hidden pores
1
The part: an aircraft wing-rib bracket that carries load from the rib into the wing spar.
2
The process: laser powder-bed fusion (metal 3D printing) in AlSi10Mg aluminium alloy, for low weight and complex shapes.
3
The catch: printing traps gas pores and leaves lack-of-fusion voids. Some porosity is always present.
4
The risk: each pore is a ready-made flaw. Under repeated flight loads it can grow into the crack that breaks the bracket.
Printed cross-section (schematic). Porosity φ = pore volume ÷ total volume.
Problem:  how much does porosity reduce the size of flaw the bracket can safely carry, and how can a designer check that quickly?
2

### Notes:
The bracket is printed, not machined, so it is light and can have an optimised shape. But printing always leaves pores. Each pore is a flaw already inside the part, and repeated flight loads can grow it into a crack. So our problem is: how much does porosity cut the flaw size the bracket can tolerate, and how can a designer check that quickly?

<!-- Slide number: 3 -->
02 · OBJECTIVE
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Estimate the critical flaw size as porosity rises
Learn the material
TARGET QUANTITY (PLANNED)
1
Train a neural network on the 73 supplied AlSi10Mg simulations to predict the stress history within the sampled temperature, strain-rate, density, G and strain ranges. Sparse conditions need extra caution.
KI(ac)  =  KIC
a
crack size for the chosen crack model (depth, radius or half-length); a CT pore needs a pore-to-crack convention
Load the bracket
2
Pass those curves into Ansys and find the stress field around the bracket's critical location. This coupling is proposed, not yet validated.
K
KI from a handbook solution or FE fracture analysis, using the stress that opens that crack, not peak von Mises
K
KIC: source and porosity dependence still to be defined (no toughness data supplied)
Estimate the critical flaw size
3
For a specified crack geometry and orientation, compute KI(a) and solve KI(ac) = KIC across porosity. Planned.
Simple Mode-I case: ac = (1/π)(KIC ⁄ Yσ)², σ = crack-opening stress. Check LEFM validity; use J if plasticity is significant.
CL here is a static critical crack size: the largest crack of the specified type that does not fracture under the given load. It is not a fatigue-life or airworthiness criterion. Study point: porosity φ = 4 % (assumed; ρ = 2592 kg/m³).
3

### Notes:
We have three objectives. First, learn the material behaviour from the 73 supplied simulations with a neural network, within the ranges those simulations cover. Second, pass that behaviour into Ansys and find the stress around the bracket's critical location; that coupling is proposed, not yet validated. Third, and still planned: estimate the critical flaw size. That needs a specified crack geometry and orientation, a stress intensity K-one of a computed from a handbook solution or a finite-element fracture analysis using the stress that opens the crack, not the peak von Mises stress, and a toughness K-I-C we have not yet sourced. The familiar formula a-c equals one over pi times K-I-C over Y sigma squared is only the simple Mode-I special case. The result is a static critical crack size, not a fatigue or airworthiness criterion.

<!-- Slide number: 4 -->
03 · OUR APPROACH
The data science life cycle we followed
01
02
03
04
05
06
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Porosity in a printed wing bracket; target CL(φ)
Bracket geometry, loads, supports; 3 team Ansys runs
73 simulations explored: coverage, trends, key inputs
JC-backbone hybrid (JC-PINN, λ = 0) selected and trained
Scored after locking on 37 held-out simulations
Planned: a bracket-check concept
WHY IT IS MULTISCALE
Material scale: the network learns how the simulated AlSi10Mg stress varies with temperature, rate, density and G.   Part scale: the team's Ansys runs load the bracket; feeding our curves into Ansys is proposed.   Decision (planned): fracture mechanics with a specified crack model turns the local stress into a critical crack size.
4

### Notes:
This is the path through the talk, following the data science life cycle. The first five stages are done: the problem, the team's Ansys runs, the data exploration, the model and its evaluation. Deployment is planned, not built. The model is a Johnson-Cook-backbone hybrid; its selected physics-loss weight is zero. It is multiscale in intent: the network works at the material scale, Ansys at the part scale, and a fracture model would turn local stress into a critical crack size. The material-to-Ansys coupling and the fracture step are still proposed.

<!-- Slide number: 5 -->
04 · CAD MODEL, LOADS AND SUPPORTS
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Rib Bracket.STEP: geometry, loads and supports
![Bracket planform with the bearing force F on the upper half of the bore, fixed supports on both mounting faces, reactions R and moment M = F × 210 mm](img_141)

| Envelope | 231.5 × 230 × 40 mm plate |
| --- | --- |
| Volume · mass | 778 cm³ · ≈ 2.1 kg at 2700 kg/m³ |
| Material | AlSi10Mg, laser powder-bed fusion |
| Load F | Bearing load along +Y on the upper half of the Ø10 mm bore (628 mm²); magnitude and load history not archived |
| Supports | Fixed on both 50 × 40 mm spar mounting faces (team set-up; not verifiable from archived files) |
| Reactions | R = F, M = F × 210 mm (static-equilibrium idealisation) |
| Load path | Truss estimate: lower arm in tension, diagonal arm in compression |

![Two bore close-ups: a load on the whole bore pulls the lower half into the hole; a pin load presses only on the upper half](img_142)
Why only the upper half? A pin can only push: it bears on the half of the bore the load drives it into, and the lower half opens a gap. Loading the whole bore would pull on the lower half and spread F over twice the area.
5

### Notes:
This slide summarises the structural set-up. The geometry is measured from the STEP file: a 40 mm thick AlSi10Mg plate with two arms meeting at a 10 mm bore, 778 cubic centimetres, about 2.1 kg at 2700 kilograms per cubic metre. The pin load F acts upward on the upper half of the bore, because a pin can only push. The team describes both spar mounting faces as fixed; we could not verify the load magnitude, load history or supports from the archived files. R equals F and the moment F times 210 mm are static-equilibrium idealisations, and the tension and compression labels come from a simple truss estimate.

<!-- Slide number: 6 -->
05 · ANSYS SIMULATIONS
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Three explicit Ansys simulations supplied by the team
Workbench project Comparison Study - Final: three Explicit Dynamics (AUTODYN) systems, each importing Rib Bracket.STEP, with different material cards. Identical load, mesh and supports could not be verified: the set-up files were not archived.
EL  A · Elastic
JC-B  B · Elasto-plastic JC
JC-U  C · User-defined JC
![Schematic elastic stress-strain line](img_165)
![Schematic Johnson-Cook hardening curves](img_170)
![Schematic of tabular (plastic strain, yield stress) rows; the team's values are not archived](img_175)
σ = E·ε
σy = (A + B εpⁿ)(1 + C ln ε̇*)(1 − T*ᵐ)
team's (εp, σy) table
Linear and never yields. Card: density, E, ν.
Ansys' built-in Johnson–Cook strength in equivalent plastic strain εp: hardening, strain-rate and temperature terms.
Multilinear hardening entered by the team; its source is unconfirmed. Ansys tables use εp, but our data and JC-PINN use total axial strain E11, so conversion needs a confirmed E.
6

### Notes:
The team ran three explicit dynamics systems in Ansys. Each imports the same bracket STEP file and uses a different material card. We could not confirm from the archived project that the load, mesh and supports are identical, because the set-up folder was not supplied. A is purely elastic. B uses Ansys' built-in Johnson-Cook strength, which is written in equivalent plastic strain. C is a multilinear hardening table entered by the team; where its numbers came from is unconfirmed. Note that an Ansys table expects plastic strain, while our data and our model use total axial strain, E11, so converting them would need a confirmed Young's modulus. The picture for C is only a schematic of table rows, not our curve.

<!-- Slide number: 7 -->
06 · ANSYS RESULTS
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Equivalent stress at t = 0.06 s
EL  Elastic
JC-B  Elasto-plastic JC
JC-U  User-defined JC
![Elastic: von Mises stress contour at 0.06 s, maximum 595.27 MPa (team screenshot)](img_197)
![Elasto-plastic JC: von Mises stress contour at 0.06 s, maximum 320.79 MPa (team screenshot)](img_203)
![User-defined JC: von Mises stress contour at 0.06 s, maximum 323.81 MPa (team screenshot)](img_209)
peak von Mises stress
peak von Mises stress
peak von Mises stress
595.27 MPa
320.79 MPa
323.81 MPa
at the fixed corner of the upper mounting face (possible constraint singularity)
around the bore, where the load enters
around the bore, where the load enters
Ansys contours supplied by the team (Ansys reports MPa). Load history, mesh convergence, energy balance and material-card provenance are not verified from the archived set-up.
7

### Notes:
These are the team's von Mises stress contours, all at 0.06 seconds; they are screenshot results, not re-run by us. The colour scales differ, so read the legend numbers. The elastic run peaks at 595.27 megapascals at the fixed corner of the upper mounting face; a peak at a fixed corner can be a constraint singularity that grows with mesh refinement. Both Johnson-Cook runs peak at about 321 to 324 megapascals around the bore. We could not check load history, mesh convergence or energy balance, because the set-up files were not archived.

<!-- Slide number: 8 -->
07 · ANSYS COMPARISON
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
The supplied JC runs have similar peak stresses at 0.06 s

### Chart: Peak von Mises stress at t = 0.06 s (MPa, team screenshots)

| Category | Peak von Mises stress (MPa) |
| --- | --- |
| EL | 595.27 |
| JC-B | 320.79 |
| JC-U | 323.81 |

Elastic peak vs built-in JC
1.86×
595.27 vs 320.79: plasticity lowers the peak by about 46 %. The elastic peak sits at a fixed corner and may be mesh-dependent.
JC-U peak vs built-in JC
0.94 %
323.81 vs 320.79. One peak at one instant does not validate the material law, the full response or JC-PINN-to-Ansys coupling.
Plastic-run peaks sit at the bore
Bore
Where the pin load enters. A fracture check would need the crack-opening stress there, not the peak von Mises value.
JC-U is the proposed route for our material curves into Ansys; the table's provenance and full response remain to be checked.
Ansys contours supplied by the team; not independently re-run. Set-up (load, mesh, energy balance) not archived.
8

### Notes:
Three observations from the team's screenshots. The elastic run's peak is 1.86 times the built-in Johnson-Cook peak, 595.27 against 320.79; plasticity lowers the peak by about 46 percent. That elastic peak sits at a fixed corner, which may be a mesh-dependent singularity. The user-defined run's peak differs from the built-in one by 0.94 percent. That is a single number at a single instant: it does not validate the material law, the full response, or any coupling from our model to Ansys, and we do not know where the user-defined table came from. In the plastic runs the peak sits at the bore. For a fracture check we would need the stress that opens a specified crack there, not the peak von Mises value.

<!-- Slide number: 9 -->
08 · EXPLORATORY DATA ANALYSIS
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
The data: 73 AlSi10Mg simulations from the professor
108
73
2.2 M
5 → 1
WHAT EACH SIMULATION GIVES
Temperature T
planned simulations
with results
rows of history
inputs → output
30 · 100 · 200 °C
Strain rate ε̇

| cases available | 10⁻⁵ /s | 10⁻⁴ /s | 10⁻³ /s |
| --- | --- | --- | --- |
| 30 °C | 9 | 9 | 9 |
| 100 °C | 9 | 9 | 9 |
| 200 °C | 1 | 9 | 9 |
| 300 °C | 0 | 0 | 0 |

10⁻⁵ · 10⁻⁴ · 10⁻³ /s
Density ρ
2488 · 2619 · 2700 kg/m³ → porosity via the assumed mapping φ = 1 − ρ/2700: 7.85 · 3 · 0 %. Physical interpretation pending the professor's confirmation
Shear modulus G
23 314 · 24 541 · 25 300 MPa (inferred)
Output
von Mises stress Svm along axial strain E11 = 0–10 %
Each cell holds 9 combinations of density × shear modulus. Only one case at 200 °C, 10⁻⁵ /s; none at 300 °C.
Units (°C, /s, kg/m³, MPa) inferred from the data, unconfirmed; stress units inferred as MPa (unconfirmed).
9

### Notes:
The professor gave us a design matrix of 108 simulations; 73 have results, about 2.2 million rows of history. Every cell of temperature and strain rate has 9 combinations of density and shear modulus, except 200 degrees at the slowest rate, which has only one case, and 300 degrees, which has none. Porosity is represented through density with our assumed mapping, phi equals one minus rho over 2700: that gives 0, 3 and 7.85 percent for the three density levels, and our 4 percent study point corresponds to 2592. Whether density really encodes porosity in this dataset still needs the professor's confirmation.

<!-- Slide number: 10 -->
09 · EXPLORATORY DATA ANALYSIS
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Temperature and strain rate drive the curves
![All 73 stress-strain curves coloured by temperature, and the strain-rate effect at 30 °C](img_301)

### Chart: Stress change for one level step (inferred MPa)

| Category | Largest stress change (inferred MPa) |
| --- | --- |
| Temperature | 22.12 |
| Strain rate | 17.45 |
| Shear modulus G | 3.4 |
| Density ρ | 0.19 |

1
Every curve ends below its starting stress: on average 138 → 68 (inferred MPa) over 10 % strain.
2
Hotter means weaker; a faster rate starts higher but softens faster, so curves cross near 6 % strain.
3
Case 60 is irregular and the only case at 200 °C, 10⁻⁵ /s. We kept it.
Mean of the largest gap between paired curves that differ in one input by one level. Stress units inferred as MPa (unconfirmed).
10

### Notes:
Left: all 73 curves. Every curve ends below where it starts, and hotter cases sit lower; that does not mean every step of every curve falls, the irregular case 60 included. Right: at 30 degrees, a faster rate starts higher but softens faster, so the curves cross. The chart compares pairs of cases that differ in one input only: one temperature step moves the curve by 22 units, which we infer to be megapascals, one rate step by 17, shear modulus by 3, and density by only 0.2. So this data says very little about porosity directly; that becomes important for the model.

<!-- Slide number: 11 -->
10 · PREPARING THE DATA
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
From raw histories to a case-wise train-test split

### Chart: 73 simulations, split by case

| Category | Split |
| --- | --- |
| Training cases | 36.0 |
| Held-out test cases | 37.0 |

Resample
1
Every curve is interpolated to the same 120 strain points (0.02–9.99 %), so slow cases with 100 000 rows don't outweigh fast ones with 1 000.
Split by case
2
Random 50/50 split of whole simulations, as the professor asked: 36 for training, 37 held out from fitting (seed 42).
Scale
3
Scaler statistics are fitted only on the 36 training cases. (The test cases were explored in earlier project stages.)
Learn
4
Each query is (T, log ε̇, ρ, G, E11) → Svm: 36 × 120 = 4 320 training points from 36 independent simulations.
All 120 points of a simulation stay on the same side of the split.
11

### Notes:
Before modelling, we resample every curve to 120 strain points so that each simulation counts equally. We split whole simulations, not rows, 36 for training and 37 held out from fitting, as the professor asked. Scaler statistics come from the training cases only, although the test cases had been explored in earlier project stages. That leaves 4,320 training points, but they come from just 36 independent simulations, which we keep in mind when judging accuracy.

<!-- Slide number: 12 -->
11 · CHOOSING THE NEURAL NETWORK
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Choosing the model: a JC-backbone hybrid

### Chart: Mean curve RMSE, training side only (inferred MPa, lower is better)

| Category | Case cross-validation (training partition) | Unseen temperature–rate groups (used in selection) |
| --- | --- | --- |
| JC equation alone | 10.238 | 13.947 |
| Plain MLP | 2.174 | 11.9 |
| JC-PINN (λ = 0) | 2.098 | 6.2349 |

JC equation alone
Readable but too rigid: case-CV 10.24, groups 13.95.
Plain MLP
Case-CV 2.17, but 11.90 on unseen temperature–rate groups.
JC-PINN (selected)
JC equation × learned correction. Physics-loss weight λ = 0: seven JC constants and the correction are fitted jointly to data.
No accuracy benefit from physics is shown. The same network with the JC equation switched off scored better (groups 5.63 vs 6.23; test 0.338 vs 0.439). We keep the JC backbone as the project's adopted governing form; its constants are fitted jointly with the correction, not independent material properties.
Group scores were used to select among 14 JC-PINN settings, and the MLP's setting was nested in its group test, so they are not independent estimates of superiority; optimism is not quantified. Curve RMSE, units inferred as MPa.
12

### Notes:
We compared approaches using only the training partition. The first bar of each pair is case cross-validation on training cases; the second is the mean over nine hidden temperature-rate groups. The JC equation alone is readable but too rigid. A plain MLP scores 2.17 in cross-validation but 11.90 on hidden groups. The selected JC-PINN, the JC equation times a learned correction, scores 2.10 and 6.23. Two things must be said plainly. First, the selected setting has physics-loss weight zero: no physics residual penalty is active; the seven JC constants and the correction are fitted jointly to data. Second, the same network with the equation switched off scored better, 5.63 against 6.23 on groups and 0.338 against 0.439 on test, so these comparisons show no accuracy benefit from the physics. We keep the backbone because the project adopted that governing form. The group scores were also used in selection, so they are not independent evidence that one model is better.

<!-- Slide number: 13 -->
12 · JC-PINN VERSUS A PLAIN MLP
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
JC-PINN versus a plain MLP

| Model | Random 37-case test | Unseen temp/rate groups (9-group mean) | Note |
| --- | --- | --- | --- |
| Plain MLP, 5-16-16-1, 385 weights | 0.143 | 11.90 | tried as an alternative; no JC backbone |
| JC-PINN (selected) | 0.439 | 6.23 | JC backbone × learned correction, λ = 0, 5 seeds |
| JC-PINN, JC equation switched off (control) | 0.338 | 5.63 | post-hoc check, not used for selection; better on both |
| JC equation alone | 7.37 | 13.95 | too rigid: same curve shape for every condition |

Familiar conditions
Unseen temperature–rate groups
On the random split the plain MLP is more accurate: 0.143 vs 0.439.
JC-PINN 6.23 vs MLP 11.90, but these scores were used in selection: not an independent test of superiority.
These comparisons do not show an accuracy benefit from the JC backbone or a physics penalty.  Random-split scores measure interpolation between near-duplicate cases; the unseen-group test is closer to real prediction. Curve RMSE, inferred MPa.
13

### Notes:
All numbers are curve RMSE in stress units we infer to be megapascals. The plain MLP, 5-16-16-1 with 385 weights, scores 0.143 on the random 37-case test and 11.90 on the nine hidden temperature-rate groups. The selected JC-PINN, physics-loss weight zero, five seeds, scores 0.439 and 6.23. The post-hoc control, the same network with the equation switched off, scores 0.338 and 5.63: better on both, and it was not used for selection. The JC equation alone scores 7.37 and 13.95. So the table does not show that the JC backbone or physics improves accuracy. The JC-PINN beats the plain MLP on hidden groups, but those group scores were part of model selection, so this is not an independent test of which model is better. Differences in architecture, output form and regularisation also prevent pinning the gap on a single ingredient.

<!-- Slide number: 14 -->
13 · DATA MODELLING
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
JC-PINN: a JC-backbone hybrid with a learned correction
σ = σJC(θ) · exp(δ)     λ = 0
![Animated: recorded JC-PINN training trace for four training cases, curves moving onto the simulation data as the loss falls](gif_training)
σJC = [A − Bεⁿ][1 + C ln(ε̇/ε̇₀)][1 − T*ᵐ][G/G₀]q[1 − φ]r
ε = E11, total axial strain (not equivalent plastic strain)
ε̇₀ = 10⁻⁵ /s  ·  T* = max[(T − 30)/(600 − 30), 0], T in °C
G₀ = 25 300 MPa  ·  φ = 1 − ρ/2700 (assumed mapping)
A − Bεⁿ is a softening form, unlike standard JC A + Bεpⁿ
δ network: 5 inputs → 16 → 16 → 1, tanh, starting at δ = 0 (the plain JC law)
1
Watch it learn: at step 0 the model is the plain JC law (lines off the dots). Adam and then L-BFGS pull the four training curves towards the simulation data as the loss falls about 60-fold (0.171 → 0.0028).
Parameters: 385 network weights and biases + 7 JC constants = 392 per member; 1 960 across 5 seeds
2
Selected λ = 0: No physics-residual penalty. Backbone and correction are not separately identifiable
3
Animated in Slide Show: recorded training trace, seed 0 (not a new run). Stress units inferred as MPa.
Training: Adam 1 500 steps, then L-BFGS ≤ 2 500 iterations; weight decay α = 1; geometric mean of 5 seeds
4
14

### Notes:
The model multiplies the custom Johnson-Cook form by exp of delta, a small neural correction. In the equation, epsilon is E11, the total axial strain of the data, not the equivalent plastic strain of standard Johnson-Cook; the reference rate is ten to the minus five per second; T-star is temperature scaled between 30 and 600 degrees and clipped at zero; G-nought is 25,300 megapascals; and porosity enters only through density, using our assumed mapping phi equals one minus rho over 2700. Note the A minus B epsilon to the n term: it is a softening form, unlike standard hardening Johnson-Cook. The selected physics-loss weight lambda is zero, so no physics residual penalty is active; the seven constants and the network are fitted jointly, and their separate contributions are not identifiable. Each member has 385 network weights and biases plus seven constants, 392 values; five members give 1,960. The animation is the recorded training trace for seed 0, not a new run.

<!-- Slide number: 15 -->
14 · EVALUATION
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Scored on 37 simulations held out from fitting
![Animated: JC-PINN prediction against each of the 37 held-out test curves, with the parity plot filling in to R² = 0.9995](gif_test)
0.4386
0.9995
mean of the 37 curve RMSEs (inferred MPa)
R² over 4 440 test points
94.9 %
37 / 37
of points within ±1 source stress unit
cases better than the JC law alone
Animated in Slide Show: each frame is one held-out case; the right panel collects every point.
How to read it: 37 simulations held out from fitting; scored after the model was locked. Not a blind test: the test cases were explored in earlier project stages. Worst curve 0.84 (case 10); pooled point RMSE 0.504. The JC law alone scores 7.37, so the correction cuts the error about 17-fold. The physics-disabled control scored 0.338 on the same cases.
15

### Notes:
These 37 simulations were held out from fitting and scored after the model was locked. It is not a blind test: the same cases were explored in earlier project stages. The animation steps through every held-out case: the orange line is the prediction, the dots are the simulation. The mean of the 37 per-curve RMSEs is 0.4386 in units we infer to be megapascals; the pooled point RMSE is 0.504; the worst curve is 0.84, case 10. R squared is 0.9995 over 4,440 points, and 94.9 percent of points are within one source stress unit. Every one of the 37 cases beats the JC law alone, which averages 7.37. For balance: the physics-disabled control scored 0.338 on the same cases.

<!-- Slide number: 16 -->
15 · EVALUATION
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Where the model is strongest, and where to be careful

### Chart: Held-out test error by temperature and strain rate (mean curve RMSE, inferred MPa)

| Category | Test RMSE (inferred MPa) |
| --- | --- |
| 30 °C · 10⁻⁵ | 0.354 |
| 30 °C · 10⁻⁴ | 0.803 |
| 30 °C · 10⁻³ | 0.182 |
| 100 °C · 10⁻⁵ | 0.434 |
| 100 °C · 10⁻⁴ | 0.283 |
| 100 °C · 10⁻³ | 0.454 |
| 200 °C · 10⁻⁴ | 0.569 |
| 200 °C · 10⁻³ | 0.143 |

Strong
Every group's mean curve RMSE is below 1. Lowest: 200 °C · 10⁻³ (0.14) and 30 °C · 10⁻³ (0.18); 100 °C · 10⁻³ is 0.45.
Weakest
30 °C · 10⁻⁴ (0.80): 8 test cases but only 1 training case at that condition.
Gaps in the data
One case at 200 °C · 10⁻⁵ and none at 300 °C: predictions there are extrapolation.
Density / porosity
Matched density steps move stress by only ≈ 0.2; backbone exponent r ≈ 0 (the correction also sees density). Porosity-labelled data are needed.
A plain MLP scored lower on familiar conditions (0.143 vs 0.439 test) but higher on unseen temperature–rate groups (11.90 vs 6.23); those group scores were used in selection, so they are not independent estimates. Stress units inferred as MPa (unconfirmed).
16

### Notes:
Broken down by condition, every held-out group has a mean curve RMSE under one unit, which we infer to be megapascals; individual points can be larger, up to 2.9. The two lowest-error groups are 200 degrees and 30 degrees at the fast rate, 0.14 and 0.18; note that 100 degrees at the fast rate is 0.45, so this is not a fast-rate rule. The weakest group, 30 degrees at the middle rate, has eight test cases but only one in training. There is one case at 200 degrees and the slowest rate and none at 300 degrees, so predictions there are extrapolation. Density barely changes the curves; the backbone's porosity exponent is about zero, although the correction network also receives density. A plain MLP was better on familiar conditions but worse on hidden groups, and those group scores were used in selection.

<!-- Slide number: 17 -->
16 · DEPLOYMENT · PARTLY BUILT, MOSTLY PLANNED
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
Planned: a bracket-check concept for aerospace companies
1
2
3
4
5
PLANNED
EXISTS
EXISTS
PLANNED
PLANNED
Company inputs
JC-PINN inference
Material card
Bracket analysis
Fracture check
›
›
›
›
CT-scan porosity and largest pore (needs a pore-to-crack convention) · temperature · load rate
Predicts Svm(E11) for given conditions, with range warnings
Writer exists (CSV / APDL / XML), untested template; E11 → εp needs a confirmed E
Validated coupling; check energy balance and load rate before treating stress as static
Specify crack geometry and orientation; KI(a) from the crack-opening stress; solve KI(ac) = KIC; check LEFM or use J
DECISION CONCEPT · PENDING FATIGUE ANALYSIS, MARGINS AND VALIDATION
STATUS ON MAIN
Accept
Inspect
Reject
Exists: locked JC-PINN inference with range warnings; porosity material-study workflow; material-card writer (unvalidated template).
Planned: validated Ansys coupling, crack model and KIC, fatigue assessment and the decision tool. The older Model Studio app is archived.
largest crack-equivalent pore well below ac
close to ac: re-scan or test
at or above ac
A static critical crack size alone is not a fatigue-life or airworthiness criterion; cyclic flight loading needs a fatigue / damage-tolerance assessment.
17

### Notes:
This slide separates what exists from what is planned. On the main branch today: the locked JC-PINN can be run for given conditions with range warnings; a porosity material-study workflow uses it; and a material-card writer can export CSV, APDL or XML tables, though it is an unvalidated template, and converting total axial strain to plastic strain needs a confirmed Young's modulus. Still planned: validated coupling into the Ansys bracket model, with energy-balance and loading-rate checks before treating explicit stresses as static; a fracture check with a specified crack geometry and orientation, a stress intensity from the crack-opening stress, and a toughness source; and the decision tool. Accept, inspect or reject is a concept only: a static critical crack size is not a fatigue or airworthiness criterion. The older Model Studio app has been archived.

<!-- Slide number: 18 -->
17 · LIMITS AND OPEN QUESTIONS
Problem
CAD & Ansys
EDA
Model
Evaluate
Deploy
What we have not shown
1
2
Evidence
Definitions unconfirmed
The test set is not blind. Case 60 (200 °C, 10⁻⁵ /s) is a single irregular case the model cannot fully reproduce. The Ansys set-up is not archived. There is no experimental validation.
Svm's physical units, spatial averaging and generating solver; Evm is not established as accumulated plastic strain; why every curve ends below its start; whether density and G represent porosity.
3
4
Porosity
CL not yet computed
Represented through density with the assumed mapping φ = 1 − ρ/2700 (cases at 0, 3 and 7.85 %; 4 % study point = 2592 kg/m³). Backbone exponent r ≈ 0, but the correction also sees density; this does not show real pores are harmless.
Needs crack geometry and orientation, a pore-to-crack convention, a KIC source, KI(a) from the crack-opening stress, an LEFM check (or J), and fatigue assessment for cyclic loads. To confirm with the professor.
18

### Notes:
Before concluding, what we have not shown. Evidence: the test set is not blind, case 60 is a single irregular case the model cannot fully reproduce, the Ansys set-up was not archived, and nothing is validated against experiments. Definitions: we have not confirmed Svm's physical units, its spatial averaging or the solver that generated it; Evm is not established as accumulated plastic strain; we do not know why every curve ends below its start, or whether density and shear modulus really stand for porosity. Porosity: it enters through density, using our assumed mapping phi equals one minus rho over 2700, which gives 0, 3 and 7.85 percent for the cases and 2592 for our 4 percent study point. The backbone's porosity exponent is about zero, but the correction also sees density, and this says nothing about whether real pores are harmless. Finally, the critical flaw size is not computed: it needs a crack model, a toughness source, a stress intensity from the crack-opening stress, a validity check, and a fatigue assessment.

<!-- Slide number: 19 -->
CONCLUSION
What we showed, and what comes next
01
02
Bracket set-up and Ansys peaks
A single-peak agreement only
With an upper-half bore load, the team's plastic runs peak at the bore. The elastic peak is 1.86× the built-in JC peak (set-up details not archived).
JC-U's peak is within 0.94 % of built-in JC. This does not validate the material law, the full response or JC-PINN-to-Ansys coupling.
03
04
An accurate JC-backbone hybrid
Next: critical flaw size · PLANNED
0.4386 mean curve RMSE on 37 held-out cases (R² 0.9995; 37/37 better than the JC law alone). λ = 0, and the physics-disabled control did better: no accuracy benefit from physics is shown.
Define crack geometry, orientation and KIC; compute KI(a) from the crack-opening stress; validate the coupling and add fatigue before any decision tool.
Ansys results: team screenshots, not independently re-run. Material-data stress units inferred as MPa (unconfirmed). No experimental validation.
19

### Notes:
To conclude. With the upper-half bore load, the team's plastic Ansys runs peak at the bore, and the elastic peak is 1.86 times the built-in Johnson-Cook peak; the set-up details were not archived. The user-defined run's peak is within 0.94 percent of the built-in one, but that single number does not validate the material law, the full response or any coupling from our model. Our JC-backbone hybrid reproduces the 37 held-out simulations to a mean curve RMSE of 0.4386, R squared 0.9995, and beats the JC law alone on every case. Its selected physics-loss weight is zero and the physics-disabled control did better, so we do not claim an accuracy benefit from physics. Next, still planned: a crack model with toughness, the stress intensity from the crack-opening stress, a validated Ansys coupling and a fatigue assessment, before any decision tool.

<!-- Slide number: 20 -->
Thank you
Any Questions?
Pranav Parasuram C  ·  R Saravanan  ·  Dinesh Y  ·  Amit Narayan K
Multiscale Modelling of Materials using Machine Learning  ·  IIITDM Kancheepuram

### Notes:
Thank you. We are happy to take any questions.
