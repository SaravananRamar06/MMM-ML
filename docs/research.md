# Choose small networks for material curves

**Current user direction, 31 October:** compare MLP with PINN after establishing
the governing constitutive equation, replacing the earlier one-model plan.
All available files are supplied. See [the physics-first Colab plan](mlp-pinn-colab-plan.md).
The format resembles VPSC output but source law/provenance are unconfirmed;
recovery/saturation is a candidate for research, not an adopted governing law.

## Current explanation for the Colab plan — 31 October 2026

The user asked why an MLP was selected. The planned single query MLP maps five
numeric features `(T, log10(rate), density, G, E11)` to continuous `Svm`.
Nonlinear hidden layers allow an empirical nonlinear response; evaluating the
same condition at successive E11 queries draws its curve. This formulation
matches the observed increasing-E11 histories without requiring spatial inputs
or demonstrating a need to learn diverse loading sequences.

Only 73 independent simulation cases are available, with 36 assigned to
training. The proposed 5-16-16-1 network has 385 weights and biases; its compact
size limits capacity relative to larger networks but does not guarantee freedom
from overfitting. Training-only scaling, L2 regularisation, case-level validation
and a simple baseline remain necessary. Scikit-learn provides CPU training
with few dependencies, useful for the requested beginner Colab notebook.
[Official MLP guide](https://scikit-learn.org/1.7/modules/neural_networks_supervised.html).

These are reasons for a starting architecture, not proof that an MLP beats
every alternative. The new notebook has not been trained. The model represents
the supplied loading family; general cyclic/multiaxial response would require
appropriate history/state information and new evaluation. Fixed assumed
porosity 4% remains study metadata and is not a learned influence.

The research snapshot below is historical. In particular, its CL=lift reading
was superseded on 27 October: the current project CL is critical flaw length.
The current Colab plan selects one neural network; older proposals for a second
network below describe the earlier comparison stage.

## Could another neural network be better? — 31 October 2026

No replacement is established for the new Colab plan. Recomputed means from
the existing `runs/score/select_*_Svm.json` records, without retraining:
query MLP CV mean curve RMSE 1.158263214; transformed-input MLP 1.535682918;
PCA-coefficient MLP with four components 2.269393103 and six components
2.004344462. Their condition-holdout means are respectively 6.793602548,
8.609057590, 11.085609443 and 11.205496577, in source stress units.
Every CV record covers the same 36 training IDs. These are historical
five-initialisation ensemble comparisons, not results of the planned single
network, and do not prove superiority over untested architectures. The
transformed-input MLP does not have a physics-informed loss.

- A small **Kolmogorov-Arnold network (KAN)** is a plausible optional comparison
  because its learnable spline functions offer a different approximation
  structure for numeric regression. The [original KAN paper](https://arxiv.org/abs/2404.19756)
  reports benefits on its own problems, not this dataset. Treat suitability
  here as a hypothesis; it needs a separate implementation and validation.
- A **physics-informed MLP** could add justified governing-law residuals or
  constraints once equations, units and states are established. This is a
  training formulation and can use an MLP backbone, not necessarily a new
  architecture. See the [original physics-informed formulation](https://arxiv.org/abs/1711.10561).
  Fixed assumed porosity of 4% supplies no missing constitutive equations.
- **Recurrent/state-based models** become relevant for general path-dependent
  response, including unloading and reloading. The supplied increasing-E11
  histories do not establish that broader task. A [physically recurrent model](https://arxiv.org/abs/2209.07320)
  demonstrates embedding actual constituent laws and internal variables for
  that purpose; its results are not evidence of superiority for this dataset.
- **DeepONet** learns mappings involving input functions through branch and
  trunk networks ([original paper](https://arxiv.org/abs/1910.03193)). The current
  finite-condition-to-strain-query problem has not demonstrated a need for
  that additional structure.

Recommendation remains the compact query MLP. If a second neural experiment
is requested, compare a small KAN with the single MLP on identical case folds,
inputs, strain sampling and original-unit curve metrics, using training-only
preprocessing and a comparable bounded tuning budget. Include training-side
condition holdouts and convergence/seed sensitivity; keep the final case
holdout out of selection and retain its historical-exposure disclosure. No
KAN, PINN or recurrent model was trained or added to the chosen notebook.

Research completed **24 October 2026**. Evidence: primary research papers, official ML documentation, and a reproducible inspection of all supplied histories.

**Later workspace update:** this report records the research-completion state. Claude has since reported implementation/experiments and created a 36/37 split; Codex has observed those artifacts but has not reproduced its results. See the latest update in [context.md](context.md). Statements below that no model/split exists describe the earlier research snapshot.

**Use a compact, regularised feed-forward multilayer perceptron (MLP) as the first material-response model.** Its proposed inputs are temperature, log strain rate, density, shear modulus, and axial strain `E11`; its output is recorded equivalent stress `Svm`. Reserve a second model for a small MLP that predicts coefficients of a compressed whole-curve representation, provided training-only reconstruction tests support that representation. This recommendation fits the observed loading family and limited number of independent cases; it is not an experimentally established winner. Neither a recurrent network nor physics-informed training is justified merely by the course title or long output files. No model has been trained and no split has been saved. **CL means coefficient of lift**: the aerodynamic target remains separate because these files supply no lift labels or established material-to-lift connection.

## The 73 cases support a fixed-path material surrogate

The matrix describes 108 combinations, but 73 histories are available, containing **2,197,000 rows**. All numerical entries are finite. Every `E11` history strictly increases and agrees with prescribed strain rate multiplied by time within maximum absolute error **4 × 10⁻⁸**. Their exact common measured strain interval is **[0.0001, 0.09999996]**. These observations support a strain-query formulation along the supplied loading path; they do not prove that the material has no memory under other paths. The [inspection script](<research_notes/Neural networks for material curves/inspect_curves.py>) and [numerical results](<research_notes/Neural networks for material curves/curve_inspection.json>) preserve the evidence.

The stress histories also contradict assumptions inherited from the old presentation. Every case finishes below its initial `Svm`; initial values span 105.374–160.3209 and final values 6.289917–95.39303 in **unconfirmed source stress units**. A standard von-Mises combination of recorded Cauchy components reproduces `Svm` to within approximately 9.85 × 10⁻⁷ relative error. However, a naive tensor equivalent-strain calculation does not reproduce `Evm`, and case 60 has 237 negative `Evm` increments while `E11` continues increasing. Therefore use `E11` as the first query coordinate, retain and flag case 60, and avoid imposing positive hardening slope, a zero-stress origin, or the historical Johnson–Cook law. The audit cannot yet explain the initial state or declining response. [Local audit notes](<research_notes/Neural networks for material curves/dataset_fit.md>).

The independent units for judging generalisation are **simulation cases**, not individual rows. Density-matched curves are particularly similar: the descriptive median curve RMSE when varying density alone is about 0.184, compared with 12.93 when varying temperature alone. These are matched comparisons in source units, not causal estimates. A random split can consequently place nearly matching curves in training and testing. Good performance would demonstrate interpolation within this design more directly than extrapolation to new regimes. No output exists for the matrix's 300-temperature level.

## A query MLP has the clearest justification

The proposed prediction contract is:

`Svm = f(temperature, log10(strain_rate), density, shear_modulus, E11)`

Hold the first four inputs fixed and evaluate successive strain queries to produce a curve. This is an empirical surrogate of the recorded response, not a general elastoplastic constitutive update. A study of elastoplastic surrogate modelling explicitly distinguishes stepwise feed-forward prediction under known, nearly monotonic loading from recurrent treatment of general loading histories. Its actual RNN predicts reduced displacement fields, so it supports the distinction rather than proving this dataset's best architecture. [Vijayaraghavan et al., 2023](https://www.nature.com/articles/s41598-023-38104-x).

Start with **5–16–16–1**, containing **385 trainable weights and biases**, smooth hidden activations as a candidate, and a scalar regression output. Standardise inputs and target using fitting cases only; log-rate encoding is a proposed way to represent the three rate decades. Exact activation, width, regularisation, optimiser, and stopping budget require internal validation. Official MLP guidance supports scaling, L2 weight penalties, and starting with few layers and neurons; its optimiser observations do not establish which optimiser wins here. [MLP documentation](https://scikit-learn.org/stable/modules/neural_networks_supervised.html).

The alternatives have legitimate uses, but none currently provides a stronger default:

| Approach | Appropriate reason to use it | Decision for these files |
| --- | --- | --- |
| Query MLP | Scalar conditions and strain queries along the observed path | First model. |
| Recurrent/state-based network | Unloading, cycles, varying multiaxial paths, or unresolved dependence on prior states | Revisit if that becomes the actual task or data requirement. |
| Physics-informed/thermodynamic model | Correct governing equations and compatible state variables/supervision | Defer until those prerequisites are established. |
| DeepONet/operator model | A demonstrated benefit from learning across loading functions or branch–trunk structure | Possible, but added structure is unmotivated so far. |
| CNN | Spatial inputs with useful neighbourhood structure | No such input representation is supplied here. |

Recurrent materials research includes GRUs trained on thousands of diverse loading paths, a substantially different task. Conversely, physics-embedded recurrent networks have succeeded with 18 curves in selected examples because known constituent laws carried internal state. Thus there is **no universal minimum dataset size** that rules recurrence in or out; matching the task and available structure matters. [Mozaffar et al., 2019](https://doi.org/10.1073/pnas.1911815116), [Maia et al., 2022/2023](https://arxiv.org/abs/2209.07320).

Physics-informed training can use an MLP backbone; it is not automatically another architecture. For example, thermodynamics-based constitutive networks use free energy, dissipation, and internal-state structure beyond ordinary stress curves. Those quantities and definitions are not established here. Likewise, DeepONet's original branch–trunk design learns operators involving input functions; predicting a curve does not alone require it. These are project-specific reasons to defer complexity, not claims that those methods always need enormous datasets. [Masi et al., 2020/2021](https://arxiv.org/html/2005.12183), [Lu et al., original DeepONet manuscript](https://arxiv.org/html/1910.03193).

## A compressed-curve MLP is the meaningful second candidate

The alternative is **four material conditions → small MLP → PCA coefficients → reconstructed stress curve** on a common strain grid. PCA describes curves using a mean curve and a few learned shape directions. A materials study used that principle to compress 61 stress samples into 15 coefficients, explicitly fitting PCA on training data only. Its inputs were microstructure images and its dataset contained 100,000 composite configurations, so neither its CNN nor its accuracy transfers to this project. [Yang et al., 2020](https://gu.berkeley.edu/wp-content/uploads/2020/03/materials_and_design_gu.pdf).

Our exploratory full-dataset decomposition captured approximately **98.94%** of centred curve variance with two components, yet case 60 still had reconstruction RMSE **10.67** in source units. Three components captured 99.964%, but these are descriptive reconstruction statistics, **not prediction scores or a selected rank**. They justify investigating compression while showing why variance retention alone is insufficient. Keep the unusual case in the comparison. [Local audit](<research_notes/Neural networks for material curves/curve_inspection.json>).

Operational PCA means, bases, coefficient scalers, and rank selection must be fitted again inside training folds. A full-data basis would reveal test-target shapes. Assess reconstruction error separately from coefficient-prediction error; if a small basis loses important features, omit this second candidate rather than forcing a second network. Official guidance specifically includes PCA among transformations that can leak information when fitted before splitting. [Preprocessing and leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html).

## Build the experiment around cases and honest evaluation

The following is a recommended implementation plan, not completed work. **Use one random split of 36 training and 37 test cases**, with proposed seed 42 recorded before training; do not retry seeds for better scores. Whole cases, including every resampled or augmented version, remain together. Full-dataset exploratory analysis has already occurred and must be disclosed: the eventual holdout was descriptively inspected, although it will be excluded from fitting and score-driven selection. Inside the training half, use three case-level folds, approximately 24 fitting and 12 validation cases per fold. This respects the professor's 50/50 requirement while providing a place to choose settings without tuning against final test scores. [Grouped validation guidance](https://scikit-learn.org/stable/modules/cross_validation.html).

| Stage | Concrete work and evidence to save |
| --- | --- |
| Define | Record feature order, `E11 → Svm` contract, units/status, loading scope, and an acceptable error criterion. |
| Prepare | Preserve raw files; save case hashes, quality flags, split IDs, and interpolation checks. Sample equal numbers of strain queries per case or normalise losses by case. |
| Validate | Within each fitting fold, fit scaling and any PCA. Compare a small predeclared set of settings and initialisations using case-averaged validation error. |
| Train | Monitor fit/validation losses; choose stopping using case-based validation. Refit selected settings on all 36 training cases for the selected budget. |
| Test | Evaluate the frozen pipeline on all 37 test cases; preserve predictions and errors without redesigning around that score. |
| Deliver | Save the complete prediction pipeline, configuration, versions, applicability statement, and a fresh-process reload check. |

Do not use automatic random-row early stopping: it can place points from the same curve on both sides. Equal case weighting prevents a 100,000-row output from dominating a 1,000-row output. A training-mean-curve reference provides a simple performance check without becoming a third neural network. Case-level learning curves and optional training-side condition holdouts can reveal sensitivity to data availability and harder prediction settings.

Report **MAE and RMSE for every curve in original source units**, their mean/median/worst values, condition-wise breakdowns, and observed-versus-predicted plots. Include case 60 and worst cases. Pooled R² is secondary because large between-condition differences can conceal errors within individual curves. Avoid percentage errors near zero. For usability, persist scalers, weights, feature order, strain grid/PCA basis if relevant, split, seeds, code/data references, versions, and predictions; verify that reloading reproduces inference. [Model persistence guidance](https://scikit-learn.org/stable/model_persistence.html).

## The defensible project claim remains narrower than the old deck

Units, generating constitutive law, initial state, and density-to-porosity meaning remain unresolved; do not silently fill them from the old presentation. The current evidence supports developing a **material-response surrogate for the supplied loading family**. It does not validate cyclic response, the missing temperature regime, physical failure predictions, or aerodynamic lift. A multiscale claim additionally needs the source simulation scale, learned effective quantity, transfer into a larger-scale calculation, and evidence validating that transfer.

For the viva, the core explanation is: **“We chose a small MLP because our observed task maps numerical material conditions and a prescribed strain query to stress along one loading family. We split by simulation case, balance curve contributions, select settings within training cases, and evaluate unseen-case curves. A second model tests whether compact whole-curve shapes improve prediction. Neither model is claimed to predict lift without aerodynamic evidence.”** The next step is to implement this controlled experiment and let validation determine its exact settings and whether the second representation earns its place.
