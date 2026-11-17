# JC-PINN and ANSYS: study handbook

Team 8 | 17 November 2026 | Locked model of 7 November 2026

## 1. Understand the whole project before its details

We approximate simulated AlSi10Mg stress histories and then use the approximation as the flow-stress law in a small-strain J2 material routine inside ANSYS. The material predictor takes temperature, prescribed strain rate, density, shear modulus and strain. The FE solver determines the spatial displacement, strain, stress and reaction fields consistent with geometry and boundary conditions. A stress-curve predictor is not an FE solver, and a successful FE solve is not an experimental strength test.

The evidence has several distinct levels: saved predictions reproduce supplied simulations; an independent implementation reproduces saved predictions; the Fortran material core reproduces the predictor; a single-element ANSYS test reproduces the offline integration; and the bracket solves. Mesh refinement then reveals a limitation: the response after yield is mesh dependent. Each level answers a different question.

Our 73 simulations are the complete supplied dataset, although 108 conditions were planned. There are 36 training and 37 test cases, split by simulation with seed 42. Each history is resampled onto 120 strains from 0.0002 to 0.0999. Hence 4320 training points are observations from 36 simulations, not 4320 independent experiments. Units are user-confirmed as degrees C, s^-1, MPa and kg/m^3; generator documentation was not seen. Nothing is experimentally validated or validated above 200 degrees C. Earlier stages explored the test cases, so the test is not blind.

## 2. Material science: what AlSi10Mg means

AlSi10Mg is an aluminium alloy designation indicating approximately 10 mass% silicon with a smaller magnesium addition; the exact composition of our material has not been measured here. Aluminium is the ductile matrix. Silicon affects solidification and the second-phase structure. Magnesium permits precipitation strengthening in suitable heat-treated states, often discussed through Mg-Si precipitation. A phase diagram describes equilibrium possibilities; rapid laser processing can produce a structure far from equilibrium. Do not infer a precipitate population from the alloy name alone.

Laser powder bed fusion melts successive powder layers. Rapid solidification, repeated heating and directional thermal gradients can create fine cellular features, Si-rich boundaries, heterogeneous melt-pool regions, residual stress and directional properties. Heat treatment can alter this structure and its mechanical response. This is general metallurgy background, supported by the primary study linked in the pack index; we have no microscopy, build-orientation evidence or heat-treatment certification for the project specimens.

Strengthening mechanisms to explain: smaller grains impede dislocations; solute atoms perturb the lattice; precipitates impede dislocation motion; higher dislocation density increases interactions. Hall-Petch, sigma_y = sigma_0 + k*d^(-1/2), is a general grain-size relation within its applicable regime, not a fitted equation in this project. Increasing temperature can assist dislocation motion and recovery. Work hardening and thermal softening compete; a falling curve alone does not identify which microscopic mechanism caused it.

Pores remove load-bearing material, redistribute stress and can initiate damage. Their size, shape, orientation, spacing and surface proximity matter. Lack-of-fusion defects and gas/keyhole-type pores are qualitatively different possible process defects. A scalar porosity fraction loses that geometric information. Consequently two parts with the same mean density can have different fatigue lives and fracture behaviour. Our model does not resolve pores or predict their nucleation, growth or coalescence.

Density is interpreted as porosity through phi = 1 - rho/2700, using a constant solid reference density. This neglects differences in composition and thermal expansion in that conversion. At phi = 0.04, rho = 2592 kg/m^3. Density here is a constitutive input; in this static displacement-driven problem its effect is not an inertia effect. No body-force claim is needed to explain the observed response.

Decision D5 assumes G(phi) = 25300*(1-phi) MPa. The Voigt uniform-strain estimate for a solid plus zero-stiffness pores gives this upper stiffness bound. A bound on effective stiffness is not a rigorous bound on the nonlinear bracket peak: localisation, geometry and yielding complicate that inference. The repository describes the resulting porosity sensitivity as a lower estimate under D5; defend it as an assumption-based estimate, not a proven lower bound on strength loss. No measured G(phi) exists here.

The supplied design varies G and density independently. Its three G levels coincide with D5 at the three porosity levels, but that coincidence does not make every simulated pair a measured physical G(phi) relationship. Separately varied inputs let us isolate model sensitivities; a real manufactured part may couple them.

## 3. Stress, strain, elasticity and yielding

The Cauchy stress tensor has normal and shear components. Decompose it into mean stress sigma_m = tr(sigma)/3 and deviator s = sigma - sigma_m*I. The von Mises equivalent stress is sigma_eq = sqrt((3/2)*s:s). In principal coordinates it is sqrt(((sigma1-sigma2)^2 + (sigma2-sigma3)^2 + (sigma3-sigma1)^2)/2). Under uniaxial stress it is |sigma11|; under pure shear tau it is sqrt(3)*|tau|; under purely hydrostatic stress it is zero.

Von Mises is a pressure-insensitive yielding measure suited to an idealised isotropic ductile metal. It is not a crack-driving tensile stress and not a brittle-fracture criterion. Real porous materials can be pressure sensitive; a J2 law with porosity-dependent flow stress does not reproduce a full porous-plasticity yield surface.

For small deformations epsilon = (grad u + grad u^T)/2 and epsilon = epsilon_e + epsilon_p. Isotropic linear elasticity gives sigma = 2G*epsilon_e + lambda_L*tr(epsilon_e)*I, where lambda_L = 2G*nu/(1-2nu), E = 2G*(1+nu), K = E/[3*(1-2nu)]. Do not confuse the Lame constant lambda_L with the physics-loss weight lambda. nu = 0.33 is assumed in the structural model. Positive elastic stability requires G > 0 and K > 0.

Yielding begins when f = sigma_eq - sigma_y(p) reaches zero, with p the accumulated equivalent plastic strain. Associated J2 flow is d epsilon_p = d gamma*(3/2)*s/sigma_eq. Since dp = sqrt((2/3)*d epsilon_p:d epsilon_p), this convention gives dp = d gamma. Plastic flow is deviatoric: tr(d epsilon_p) = 0. This expresses plastic incompressibility of the idealised matrix law; it is not a pore-volume evolution model.

Hardening means H = d sigma_y/dp > 0; perfect plasticity H = 0; softening H < 0. Isotropic hardening changes the yield-surface radius; kinematic hardening translates it and is relevant to reversal/Bauschinger effects. Our routine uses isotropic hardening/softening, with monotonic source histories. Cyclic ratcheting, damage accumulation and fatigue are not calibrated.

Engineering strain is extension divided by initial length. Logarithmic strain is ln(L/L0). Before necking, in a homogeneous uniaxial test with approximately conserved volume, sigma_true = sigma_eng*(1+epsilon_eng) and epsilon_true = ln(1+epsilon_eng). These conversions cannot repair an arbitrary post-necking curve or reveal the source solver's unknown definitions. The project target is Svm along E11. E11 is total axial strain; reading it as equivalent plastic strain in the FE flow law is an explicit modelling approximation, not an identity established by the data.

## 4. Derive the finite-element equations

Start with quasistatic balance div(sigma) + b = 0, displacement u = u_bar on Gamma_u, traction sigma*n = t_bar on Gamma_t. Multiply by a virtual displacement v that vanishes on Gamma_u and integrate by parts:

Integral_V epsilon(v):sigma dV = Integral_V v.b dV + Integral_Gamma_t v.t_bar dA.

Approximate u = N*d and epsilon = B*d. The element internal force is f_int,e = Integral_Ve B^T*sigma dV. Assemble the global residual R(d) = f_ext - f_int(d). For linear elasticity K = Integral B^T*C*B dV and K*d = f_ext after applying displacement constraints. For nonlinear response, at iteration i solve K_t(d_i)*Delta d = R(d_i), update d and repeat. With prescribed displacements, solve the free degrees of freedom and recover reactions at the constrained ones.

This derivation explains four things an examiner may probe. Shape functions interpolate displacement; their derivatives map nodal displacement to strain. Numerical quadrature evaluates element integrals at integration points. The material law is evaluated locally at each point, while equilibrium is solved globally. A converged global residual says little about the correctness of a constitutive assumption.

SOLID186 is the quadratic 3D solid family used by the bracket, including degenerate wedge forms in this mesh. The saved baseline uses full integration. Quadratic interpolation can represent curved geometry and bending better than a comparable coarse linear mesh, but does not guarantee accuracy. Distortion, Jacobian quality, aspect ratio, integration scheme and boundary resolution all matter. Reduced integration can introduce zero-energy hourglass modes in susceptible formulations; full integration can be expensive and locking must still be considered. Near-incompressible plastic flow is a reason to examine volumetric behaviour and appropriate formulations, not proof that this specific run locks.

An unconstrained 3D body has six rigid-body modes. Supports must remove the unwanted modes without inventing physical stiffness. A perfectly fixed face is an idealisation of a joint. A sharp transition between fixed and free boundaries or an abrupt displacement patch may create singular/stress-concentrating fields. A pointwise maximum stress can rise under refinement even when global stiffness converges. Element-centroid values reduce nodal extrapolation/averaging issues but do not remove a continuum singularity.

## 5. ANSYS setup: what actually ran

The archived Workbench project was used to construct MAPDL 2024 R1 batch decks. The baseline has 7304 SOLID186 elements, fixed support and imposed UX = -2 mm, small-strain kinematics (NLGEOM off), PCG and automatic substepping. The reported 14 substeps, 40 equilibrium iterations and one bisection for USERMAT are numerical history, not physical experiments. The source deck's compact element block was converted to a compatible standard block without changing connectivity or attributes.

Do not recite conflicting node/support counts from older summaries: the baseline and mesh-study writeups use different reported node-set conventions. For a detailed defence use the actual deck and counted active sets; this preparation uses element counts and the verified load/support descriptions. No invented contact coefficient, service load, bolt preload or gravitational load is part of the explanation. A bracket title alone establishes none of them.

The original structural study condition is T = 100 degrees C, prescribed rate = 1e-4 s^-1, rho = 2592, G = 24541 MPa and nu = 0.33. E = 65279.06 MPa follows from G and nu. The later D5 coupled 4% condition uses G = 24288 MPa, so E = 64606.08 MPa. These are different cases. The 22 degrees C reference temperature in the deck does not replace the fixed 100 degrees C USERMAT input when ITEMP = 0.

The three baseline materials were elastic Workbench, a hardening MISO card, and JC-PINN USERMAT. They have different stiffnesses and yield/flow curves. The Workbench elastic E is 76600 MPa, whereas USERMAT returns its own stiffness. The stiffness ratio is 0.852. Thus the initial bracket stiffness difference has a simple elastic explanation; it is not a demonstrated neural-network effect. The hardening card's provenance and condition are not established, so it is a numerical comparator, not ground truth for validation.

In consistent mm-N-MPa mechanics, 1 MPa = 1 N/mm^2. Reaction from stress integrated over area is N, then divided by 1000 for kN. USERMAT's density input remains kg/m^3 because it is explicitly a model feature; do not confuse it with a solver mass-density entry. In an mm-N-s system a separate inertia density would need consistent mass units. This matters if dynamics is added later.

## 6. The material predictor, taught from the equation

Equation 1 is sigma_JC = (A-B*epsilon^n)*(1+C*ln(rate/rate0))*(1-Tstar^m)*(G/G0)^q*(1-phi)^r. Tstar = max(0,(T-30)/570), rate0 = 1e-5 s^-1, G0 = 25300 MPa, phi = 1-rho/2700. The minus sign implements the supplied softening strain histories; classic hardening Johnson-Cook uses a plus sign. We have not established why the unknown generator produced softening.

A and B have stress units for dimensionless strain; n, C, m, q and r are dimensionless. Every logarithm or power ratio has dimensionless argument. Differentiating the strain factor gives -B*n*epsilon^(n-1), negative for B,n > 0. Set B = A*beta/0.1^n with 0 <= beta <= 0.99. Then for 0 <= epsilon <= 0.1 the factor is A*[1-beta*(epsilon/0.1)^n] >= 0.01*A > 0. Positivity is a range-specific result, not a proof for arbitrary strain or temperature.

Why the equation is insufficient: all non-strain factors multiply the same strain shape. At fixed parameters, sigma(epsilon2)/sigma(epsilon1) cancels temperature, rate, G and porosity. The supplied curves have condition-dependent shape, so a separable product cannot fit all of them well. A flexible correction is motivated by this structural limitation.

One member predicts sigma_k = sigma_JC(theta_k)*exp(delta_k). The correction delta is a 5-16-16-1 tanh network receiving standardised T, log10(rate), rho, G and E11. A dense layer computes W*x+b and tanh supplies nonlinearity. Scaling prevents large input magnitudes dominating optimisation. Training statistics must be learned within each training fold. The backbone uses natural log of a rate ratio; the network feature uses log base 10. Confusing them changes the model.

Count network parameters: (5*16+16) + (16*16+16) + (16*1+1) = 385. With seven jointly trained constants each member has 392 trainable parameters; five have 1960. The final output layer starts at zero, so delta = 0 and exp(delta) = 1 initially. The trained correction need not be close to one merely because it started there.

The final ensemble is geometric: sigma_hat = exp[(1/5)*sum_k(ln sigma_JC(theta_k)+delta_k)]. This differs from an arithmetic mean. It averages log stresses, preserves positivity when each backbone is positive, and limits the arithmetic dominance of a high-valued member. Each member has different joint constants; averaging constants and using one network is not equivalent. Member spread measures agreement between fitted copies, not calibrated confidence or a bound on model bias.

## 7. Loss, training, selection and statistical criticism

The tested objective is normalised stress MSE + lambda*physics residual MSE + alpha/N*sum W^2. The selected model has lambda = 0 and alpha = 1, with constants trained jointly. The loss is in normalised stress space; logarithms describe the output parameterisation/ensemble, not a replacement of the data loss by log-stress MSE. Adam performs 1500 steps, followed by L-BFGS with a 2500-iteration limit. Backpropagation uses the chain rule to differentiate the objective; automatic differentiation is differentiation of program operations, not finite differences.

Candidate physics losses compared level residual delta with trend residuals involving derivatives of delta with respect to condition inputs. There were 4096 collocation points for penalised candidates, including temperatures to 300 degrees C. Such points contain no observed stresses and are not additional simulations. At the selected lambda = 0 they impose no penalty anywhere. Therefore neither physics-loss enforcement nor validation above 200 degrees C may be claimed. The most precise description is a physics-structured or equation-backbone neural model, retained under the project name JC-PINN; it is not a PDE-residual PINN solving bracket equilibrium.

Fourteen candidates combine seven physics settings with frozen/joint constants. Three case folds and nine T/rate group holdouts use only the 36 training cases; each candidate uses three seeds. The balanced score is 0.5*(case CV RMSE + group-holdout RMSE). The winner's values are 2.098, 6.235 and 4.166 MPa. Final fitting uses five members, then fingerprints equation.json before the formal test read.

Why a split by case matters: neighbouring strains on one curve share the same simulation and condition. Splitting points leaks near-duplicates and makes the test look easier. Why group holdouts matter: a random case split often contains similar condition combinations in training, whereas hiding a whole temperature/rate group is harder. These holdouts are still inside the training dataset and involved in selection. They are not an independent estimate of arbitrary extrapolation, and selection/development reuse makes them somewhat optimistic. The final test protocol prevents new test-based selection, but cannot erase earlier knowledge of the same test cases.

Per-case RMSE_i = sqrt[(1/120)*sum_j(error_ij^2)]. The reported main metric is mean_i RMSE_i, not sqrt of all squared errors pooled together. R^2 = 1-SSE/SST is also sensitive to the target range; a high R^2 does not establish safe extreme-condition predictions. Signed bias can cancel large positive and negative errors. Report RMSE, worst cases, local trends and relevant holdouts together.

The locked mean test curve RMSE is 0.439 MPa, R^2 0.99952, median 0.395, worst 0.841, bias +0.009 and 94.9% of test points within 1 MPa. Equation 1 alone gives 7.37 MPa. However the no-equation control gives 0.338, the earlier single MLP 0.143, and earlier ensemble 0.059 MPa. The control also beats JC-PINN on group holdouts. Consequently this study does not demonstrate an accuracy benefit from Equation 1. Structure, named factors and a physical initialisation remain useful, with joint-parameter identifiability limits.

Identifiability: if a backbone parameter change can be offset by delta, different decompositions can predict nearly the same stress. Joint constants are not independently measured material constants. To describe the standalone calibrated law, use its fitted values (A 148.77, B 526.23, n 0.828, C 0.0292, m 1.11, q 0.717, r 0), not an average of joint parameters stripped of their networks.

## 8. From scalar curve to J2 USERMAT: derive the local solve

A scalar flow-stress function alone does not specify a multiaxial constitutive model. The wrapper adds isotropic elasticity, pressure-insensitive J2 yielding, associated flow, isotropic evolution, strain mapping and an integration algorithm. Those are constitutive assumptions in addition to the neural surrogate. Multiaxial and unloading validity do not follow from fitting monotonic axial histories.

At each material point: retain the old plastic strain and p_n, compute sigma_trial = sigma_n + C_e:Delta epsilon, split mean/deviatoric stress, and obtain q_trial = sqrt(3/2*s_trial:s_trial). Evaluate f_trial = q_trial - sigma_y(p_n). If f_trial <= 0, accept the elastic state. Otherwise return along the trial deviatoric direction.

For associated J2, Delta epsilon_p = Delta p*(3/2)*s_trial/q_trial. Elastic correction is 2G*Delta epsilon_p = 3G*Delta p*s_trial/q_trial. Hence s_new = [1-3G*Delta p/q_trial]*s_trial and q_new = q_trial - 3G*Delta p. Enforce yield consistency with g(Delta p) = q_trial - 3G*Delta p - sigma_y(p_n+Delta p) = 0. Its derivative is g' = -3G-H, where H = d sigma_y/dp. Newton updates Delta p <- Delta p + g/(3G+H), with safeguards and a nonnegative admissible bracket.

The hydrostatic part stays unchanged during this ideal J2 plastic correction. A negative H can still have 3G+H > 0, allowing a well-conditioned local scalar solve. That does not prove global stability or mesh independence. The implementation safeguards the root and requests increment reduction when the solve fails. Smaller increments can address integration/convergence difficulties; they cannot regularise a spatially ill-posed softening law.

For one member, d sigma/dp = exp(delta)*[d sigma_JC/dp + sigma_JC*d delta/dp]. For the ensemble, d sigma_hat/dp = sigma_hat*mean_k[d ln(sigma_k)/dp]. tanh'(z) = 1-tanh(z)^2 supplies analytic derivatives. If standardisation is z_p = (p-mu_p)/s_p, the chain rule includes 1/s_p. Outside the strain interval the routine holds flow stress constant, so its slope is zero there.

The consistent algorithmic tangent is C_alg = partial sigma_(n+1)/partial Delta epsilon for this discrete update, with old state fixed. It is not simply the elastic tensor or scalar H, and it is not just a continuous plastic tangent copied without differentiating the return map. It drives global Newton convergence. Finite-difference verification perturbs strain increments from the same old state and compares stress changes; a perturbation crossing the elastic/plastic branch needs careful interpretation.

USERMAT receives strain increments and history and returns stress, tangent and state variables. Here SVAR1 is equivalent plastic strain, SVAR2 flow stress, SVAR3 persistent range flags and SVAR4 local Newton iterations. Flag bits are 1 for p > 0.0999, 2 for an out-of-data condition, 4 for 200 < T <= 300 degrees C. They combine by bits and persist; zero current violations do not erase earlier ones. Flow stress is held at its endpoint below p = 0.0002 and above p = 0.0999. A flat extension is an implementation choice, not learned perfect plasticity.

The strain-rate feature is prescribed at 1e-4 s^-1 in the bracket; it is not computed from local Delta p/Delta t. Therefore changing a static load-step duration does not constitute a test of calibrated viscoplasticity. Thermal tangent terms are zero and this is not a fully coupled thermo-mechanical model. Only the 3D USERMAT wrapper is supplied; plane strain and axisymmetric forms with three direct components are supported, not plane stress, shells or beams. Simply setting sigma33 = 0 is insufficient for a correct plane-stress return algorithm.

## 9. Interpret the bracket and mesh study

The coarse USERMAT bracket peaks at 190.4 kN at |UX| = 0.455 mm and reaches 136.7 kN at -2 mm. These are imposed-displacement reactions, not prescribed service forces. Elastic and hardening material curves are different comparisons. The numerical peak cannot be called ultimate load, failure load or a design allowable: there is no damage/fracture criterion, no experimental validation and no converged post-yield response.

Uniform h-refinement changes 5 mm to 2.5 mm and 7,304 to 58,432 elements. This is subdivision of the same discretised geometry, not a new CAD remesh. Initial stiffness changes -0.07%, but the peak falls -7.7% to 175.6 kN and max element EQPS rises from 0.36 to 0.99. The hardening EP force comparison changes at most 0.3%, although its peak local strain still increases. This supports softening as the main source of the large force dependence, while the displacement patch also affects local concentration.

Why softening is mesh sensitive: deformation can concentrate in a band one element wide. If the same stress-strain law is used for every element size, dissipated work per unit crack/band area is approximately h*Integral sigma d epsilon_inelastic over a chosen finite softening interval. It scales with h. Refinement changes the energy cost of localisation. This heuristic motivates a length scale/energy regularisation; it does not turn the fitted curve into a measured fracture-energy law. Our flat tail also supplies continuing plastic dissipation rather than a calibrated complete failure law.

Regularisation choices for future work include fracture-energy/characteristic-length scaling, nonlocal or gradient plasticity/damage, and an appropriately calibrated phase-field/cohesive formulation. They need extra physical parameters and implementation validation. Viscosity may stabilise a calculation, but rate regularisation must be calibrated and spatial objectivity checked. No regularisation is included in the submitted model.

The final reactions on the two meshes differ only +0.7%. This isolated agreement is misleading: much of the yielded region is already beyond p = 0.0999 on the held-constant tail, while intermediate reactions differ substantially and local strains grow. Convergence must concern the relevant full response and field measures, not a convenient endpoint. Two meshes diagnose sensitivity; they do not justify Richardson extrapolation when asymptotic convergence is absent.

Small-strain kinematics are an additional limitation when computed local EQPS approaches one. Large local strain does not by itself establish a reliable finite-strain solution. Turning NLGEOM on later would require checking the constitutive frame and finite-deformation suitability; it is not an automatic repair of the total/plastic strain mapping or softening regularisation.

## 10. Porosity, fracture and what the study cannot claim

In the supplied curves, changing density alone from phi 0 to 7.85% lowers stress by 0.34% on average; the model gives 0.31%. The fitted standalone porosity exponent is zero because that small effect is masked by the much larger backbone misfit. Zero fitted r does not imply zero porosity physics; the neural correction depends on density.

On the bracket with G fixed, peak reaction changes -0.16%. With D5 coupling G and density it changes -2.86%, and reaction at -2 mm changes -6.04%. The latter comparisons inherit mesh dependence and the assumed G(phi). A density-only partial sensitivity is different from a total derivative along a physical relation: d sigma/d phi = partial sigma/partial rho*(-2700) + partial sigma/partial G*(-25300) under D5, keeping other inputs fixed. Structural reaction adds redistribution and evolving plasticity, so its derivative is not just this pointwise stress derivative.

CL means critical flaw length. Introductory mode-I LEFM uses K_I = Y*sigma_remote*sqrt(pi*a), giving a_c = (K_IC/(Y*sigma_remote))^2/pi under those assumptions. a may mean half-length or depth depending on the geometry definition. Required inputs include a real flaw geometry, orientation, appropriate tensile stress, toughness and constraint. Von Mises stress is not interchangeable with crack-opening stress. We have no established service load or project-specific toughness, so no numerical CL is defensible.

LEFM also needs small-scale yielding. The illustrative plane-stress plastic-zone radius is r_p = (K_I/sigma_y)^2/(2*pi); plane-strain estimates are smaller. If the plastic zone is not small compared with flaw and ligament dimensions, use an appropriate elastic-plastic fracture framework, such as J-integral/CTOD with qualified resistance data. Under linear elasticity J = K_I^2/E', with E' = E for plane stress and E/(1-nu^2) for plane strain. No J calculation or crack-growth validation is delivered here. Fatigue life additionally needs cyclic loading and suitable fatigue/crack-growth data; static softening is not an S-N curve.

## 11. The strongest defensible conclusion

We delivered a locked equation-backbone surrogate of supplied simulations and verified its numerical transfer into ANSYS. We quantified its predictive errors, disclosed that a no-equation control performs better, and demonstrated that unregularised softening prevents a mesh-independent post-yield bracket interpretation. The next scientific needs are generator provenance, experimental material characterisation, justified multiaxial/strain mapping, regularisation, and structural/fracture validation. These are future work; the submitted model remains unchanged.

## 12. Advanced extension: questions beyond the exact implementation

### Thermodynamic admissibility is stronger than positive stress

For an isothermal small-strain material, a dissipation inequality can be written D = sigma:epsilon_dot - psi_dot >= 0, where psi is free energy per volume. An elastic free energy and evolution laws must be specified to assess the full inequality. J2 associated flow with nonnegative plastic multiplier and positive flow stress gives nonnegative plastic stress power sigma:epsilon_dot_p = sigma_eq*p_dot, but if stored internal-variable energy is introduced, its rate also enters dissipation. A positive exp(delta) by itself does not prove thermodynamic consistency, convexity, stability or mesh objectivity. No learned free-energy potential or complete thermodynamic identification is part of our surrogate.

### Positivity and monotonicity are different constraints

Even if the backbone has the desired sign, its correction can change derivatives. For a condition x, partial ln(sigma)/partial x = partial ln(sigma_JC)/partial x + partial delta/partial x. With lambda=0 the network derivative is unconstrained by a physics penalty. Saved sign checks sample points and support empirical behaviour within the tested box; they are not an analytic guarantee for every input. Positive stress, correct trend at sampled points and accurate generalisation are three different properties.

### Plastic modulus versus observed tangent modulus

In uniaxial loading, total strain increment d epsilon = d sigma/E + dp, and d sigma = H*dp for the flow curve. Rearranging gives the elastoplastic uniaxial tangent E_t = E*H/(E+H), provided the denominator is nonzero and the branch is admissible. Conversely H = E*E_t/(E-E_t). A slope measured against total strain is therefore not generally the plastic hardening modulus. This derivation exposes why the source E11-to-plastic mapping deserves scrutiny. It is a general one-dimensional relation; it is not a correction we have applied to the locked model.

### Unloading, stored energy and hysteresis

In this J2 wrapper, unloading from a plastically deformed state initially follows elastic stiffness while p stays fixed until yielding resumes. Residual plastic strain remains. The monotonic surrogate does not identify kinematic hardening, cyclic degradation or reversal effects. Under displacement control, integral F du is external work. During non-proportional/unloading paths it need not all be dissipation because elastic energy can be recovered. Numerical damping, artificial stabilisation or contact work, if introduced in future models, would require separate energy accounting.

### Engineering softening, necking and constitutive softening

A falling engineering tensile stress after maximum load can reflect specimen necking even when local true flow stress continues to harden. Our target is Svm along E11 in supplied simulation histories, not an independently characterised homogeneous true-stress/plastic-strain coupon law. Therefore observing a descending source history does not establish a local damage law. A defensible identification would use source definitions and, where necessary, inverse analysis of a specimen with local measurements. The selected minus-sign law is a project choice that reproduces these histories.

### Buckling is a different instability question

Elastic eigenvalue buckling linearises a stability problem around a reference state and finds load multipliers associated with a singular tangent. It does not predict general imperfection-sensitive ultimate load, and a descending reaction from material softening is not automatically buckling. A nonlinear buckling assessment needs relevant geometry, imperfections, geometric nonlinearity and an appropriate material model. No buckling result is part of the saved bracket evidence; do not claim one from a contour or a force peak.

### Thermal softening is not thermal stress

The predictor changes flow stress with its temperature input. Thermal stress additionally needs thermal expansion, temperature fields and constraints. In a simple fully restrained 1D elastic bar with uniform heating and constant properties, sigma = -E*alpha_T*Delta T. A freely expanding bar has zero thermal stress under those ideal assumptions. Our fixed-temperature USERMAT run does not establish a coupled thermal analysis, a thermal-expansion coefficient or residual stresses from printing. A temperature-dependent strength curve is not enough to supply them.

### Contact and joint idealisation

If a future bracket model includes contact, unilateral normal constraints enforce nonpenetration and friction relates tangential traction to normal pressure and slip under an assumed law. Penalty methods permit small penetration with a penalty stiffness; multiplier methods introduce constraint unknowns. These choices affect conditioning and sometimes apparent stiffness. Our defence should describe the actual inherited supports and imposed patch; no friction coefficient, bolted-joint compliance or verified contact law has been identified here. An examiner asking about a realistic joint is asking for a missing modelling layer, not a hidden project result.

### Sensitivity, uncertainty and safety factors

Sensitivity asks how a result changes when an input changes, locally or over a specified range. Uncertainty quantification assigns or bounds uncertainty in inputs, model discrepancy and predictions. A sensitivity sweep is not automatically a probability distribution or reliability estimate. Statistical variation in pores, build conditions and toughness has not been characterised. A conventional yield safety ratio allowable/sigma_eq assumes an appropriate allowable and stress solution; using a local flow stress and a mesh-dependent peak is not a certified margin. No numerical safety factor is reported.

### Numerical conditioning and near-incompressibility

As nu approaches 0.5 in isotropic elasticity, K/G becomes large, making volumetric and deviatoric scales very different. Displacement formulations can suffer volumetric locking; suitable mixed/selective formulations can help in applicable settings. The assumed nu=0.33 does not itself create an almost-incompressible elastic solid, although associated J2 plastic flow is deviatoric. A consistent tangent aids nonlinear iteration but cannot fix a poor mesh, ill-conditioned constraints or an unsuitable element formulation.

### What an actual micro-to-macro homogenisation would require

Choose a representative volume containing a statistically representative pore/microstructure population and justify separation between microstructural and structural length scales. Define macroscopic stress and strain as appropriate volume averages. For an energetically consistent scale transition, the Hill-Mandel condition equates macroscopic stress power with averaged microscopic stress power under compatible boundary conditions. Uniform displacement, uniform traction and periodic micro-boundary conditions are distinct choices; finite cells may give different estimates. Voigt assumes uniform strain and gives an elastic stiffness upper estimate; the corresponding uniform-stress Reuss construction is a compliance-based lower estimate and can become uninformative with zero-stiffness voids. Our scalar D5 assumption is not an RVE calculation or a verified homogenisation of measured pores.

### Frame indifference, invariants and loading-path transfer

A physical isotropic constitutive law should not change its scalar yielding prediction when the coordinate axes are rotated consistently: the J2 invariant supplies that property for the yield measure. At finite rotations a stress-update algorithm also needs an appropriate objective frame/rate or finite-deformation formulation. A scalar fit to monotonic uniaxial data does not identify path-dependent multiaxial behaviour. Nor does small network prediction error establish convexity of a yield surface or stability of a boundary-value problem. Our wrapper supplies explicit assumptions for these missing dimensions; their physical validity needs additional evidence.

### What rigorous future validation would look like

First define the intended prediction task and acceptance quantities before obtaining new data. Characterise the material/process state and units; test monotonic response at relevant conditions with independent cases; identify elastic/plastic measures; validate multiaxial/unloading assumptions if needed; obtain a regularisation scale or fracture-energy basis; verify integration and FE discretisation; and finally compare bracket displacements/reactions against controlled experiments with realistic joints. For fracture or fatigue add the corresponding qualified crack/cyclic data. This is a proposed programme, not work performed or permission to alter the locked submission.
