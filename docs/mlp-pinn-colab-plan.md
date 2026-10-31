# Colab plan: governing equation first, then MLP versus PINN

31 October 2026. User-requested plan; no new neural network has been created.
This replaces the earlier single-model Colab proposal. The user explicitly
requires a governing equation before either model is created and confirms
that all available files have already been supplied.

## Starting evidence

- Dataset: 73 histories plus the 108-case matrix; only OUT and CSV files.
  Preserve the fixed 36-training/37-test split and its exposure history.
- Intended prediction remains Svm against E11 at specified temperature,
  strain rate, density and G. Units, strain measures, initial state and the
  generating constitutive law have not been established authoritatively.
- The existing audit shows nonzero initial stress and lower final stress in
  every history. E11 increases; Evm reverses in case 60. Neither E11 nor Evm
  can automatically be called accumulated plastic strain.
- Porosity 0.04 is a fixed assumed study condition. It is not a verified label
  for these histories or a justification for changing their density/modulus.
- STR_STR.OUT and several column labels resemble LANL VPSC outputs. Public
  VPSC output also includes fields/order differences. This is an investigative
  lead, not identification of the supplied generator, version or hardening law.
  Public VPSC supports several hardening/state-evolution choices.
- A narrow read of the bracket's SYS/ds.dat found tabulated multilinear
  isotropic plasticity (TB,PLAS,...,MISO). This does not establish which law
  generated the professor's histories or validate the ANSYS solution.

## Phase A: establish a complete constitutive equation

1. **Create the Colab data-inspection section.** Upload the existing raw ZIP
   to Drive, copy/extract it under /content, inventory cases and load the saved
   split. No neural architecture or training is created at this stage.
2. **Write a physical data dictionary.** Review TIME, E11, Evm, Svm, stress
   components, TEMP and matrix conditions; distinguish observed relationships
   from assumed units/definitions. Establish the physical interpretation of
   the loading coordinate and initial state needed by a candidate law.
3. **Research the constitutive law.** Use original material-model papers and
   official solver references. Investigate a storage/recovery or saturation
   law first because it can represent a decreasing response from an initial
   state above saturation. Do not adopt Johnson-Cook hardening, a zero-stress
   origin, monotonic hardening, or Hooke's law applied directly to Svm/E11
   without a compatible physical derivation.
4. **Qualify a candidate before adopting it.** A literature-grounded candidate
   to investigate is the Kocks-Mecking saturation-form relation

   `d(sigma_f)/dp = theta_0 * (1 - sigma_f/sigma_sat)`

   with a specified initial flow stress. Here p is the applicable plastic
   strain coordinate, not an automatic renaming of E11 or Evm. A branch with
   sigma_f initially above sigma_sat decreases algebraically; whether that
   branch describes these simulations is an unverified hypothesis. Determine
   a justified temperature/rate/modulus dependence, initial-state treatment,
   stress-target mapping and parameter units. It is not the confirmed source
   law or an established AlSi10Mg/4%-porosity model.
5. **Calibrate and check without a neural network.** Fit candidate parameters
   using fitting cases only, including recalibration inside each validation
   fold. Assess curve shapes, residuals, parameter identifiability, numerical
   integration and temperature/rate transfer. Keep case 60 in the analysis.
   Per-case fits are shape diagnostics, not predictors for new conditions.
   Do not tune a law or its parameters using the 37 test targets.
6. **Freeze the physics specification.** Before creating either network,
   document the full governing equations, coefficients/functions, initial
   conditions, state variables, units, sources, assumptions and valid range.
   Every state/initial value must be available at inference or estimated from
   training data; do not supply a held-out case's true initial stress as a
   hidden extra input. If a candidate conflicts with the data or its variables
   cannot be established, revise the physical hypothesis before PINN training.
   An empirical smoothness penalty or von-Mises identity alone is not this
   constitutive specification. A selected literature hypothesis remains an
   assumption, not proof of the original generating law.

## Phase B: build the controlled Colab comparison

7. **Prepare identical examples.** Interpolate each case to the existing 120
   E11 points, 0.0002 to 0.0999, after checking support. Preserve case IDs and
   equal curve weights. Fit all scalers on fitting cases only. Keep phi=0.04
   as assumed metadata. The initial five inputs remain T, log10(rate), density,
   G and E11; resolve any required physical state inputs in Phase A.
8. **Use PyTorch for both models.** This updates the earlier scikit-learn-only
   proposal so both models share the same training machinery and PINN losses
   can use automatic differentiation. Begin with a shared 5-16-16-1 tanh
   backbone (385 parameters) only if the qualified law closes at the scalar
   stress level. If internal states are necessary, first document and match
   the stress backbone, required inputs and extra output/state capacity.
9. **Keep the loss comparison explicit.** Both receive the same labelled
   cases, initial-state information, scaling and regularisation:

   `L_MLP = L_data + lambda_reg * L_regularisation`

   `L_PINN = L_MLP + lambda_phys * L_equation`

   L_equation is the residual of the frozen constitutive system, including
   its applicable initial/boundary constraints. Convert derivatives back to
   physical units with the scaling chain rule, then nondimensionalise residual
   components. Use collocation points inside supported fitting-case domains;
   do not use held-out stresses, internal states or test-derived coefficients.
   This is a material-point/constitutive PINN comparison, not a 3D equilibrium
   PINN: the supplied histories contain no spatial fields for that PDE task.
10. **Select and train fairly.** Use the same three internal case folds,
    paired random initialisations, optimiser family and comparable bounded
    tuning effort. Freeze the shared optimiser/stopping configuration after
    Phase A establishes the residual and state dimension. Choose physics
    weights on validation cases; include lambda_phys=0 to verify equivalence
    to the data-only baseline. Track separate loss components, convergence,
    wall time and seed sensitivity. Never choose settings by final test error.
11. **Evaluate frozen models.** Refit selected settings on all 36 training
    cases, then evaluate the 37 test cases. Report original-unit per-curve
    MAE/RMSE, median/worst errors, condition breakdowns and physics residuals
    for both models. Show representative/worst curves and case 60 separately.
    Include training-side withheld temperature/rate diagnostics. Evaluate the
    calibrated equation alone as a non-neural reference. Disclose the prior
    holdout exploration; do not promise PINN superiority or physical validation.
12. **Save and verify.** Persist the equation specification, assumption file,
    data hashes, split/folds, configurations, dependency versions, seeds,
    scalers, checkpoints, histories, predictions, metrics and plots in a new
    dated Drive folder. Test derivative scaling against an analytical example,
    lambda=0 equivalence, split isolation, known-equation residuals and model
    reload consistency. Run the notebook from a fresh Colab runtime. Publish
    code, equation decisions and verification evidence to GitHub; exclude raw
    data, credentials and scratch files. CL/fracture prediction is a later task.

## Primary references and their limits

- [LANL VPSC source](https://github.com/lanl/VPSC_code/blob/main/vpsc8main.for)
  and [output writer/slip calculations](https://raw.githubusercontent.com/lanl/VPSC_code/main/vpsc8sub.for):
  support the format lead and multiple possible state/hardening choices, not
  provenance of the user's files.
- [Bouaziz, storage/recovery and Kocks-Mecking equations](https://arxiv.org/pdf/1202.6006):
  supplies a candidate constitutive family; no coefficients or AlSi10Mg
  applicability are transferred from the paper.
- [Sandia Johnson-Cook reference](https://www.sandia.gov/files/sierra/SM_LAME_5_20/main/models/johnson_cook.html):
  distinguishes plastic-state/rate definitions and thermal coupling; not proof
  that Johnson-Cook generated these data.
- [Physics-informed formulation](https://arxiv.org/abs/1711.10561) and
  [PyTorch automatic differentiation](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html):
  support residual-based training and its implementation, not a missing law.
