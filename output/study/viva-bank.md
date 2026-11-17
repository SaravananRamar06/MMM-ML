# Advanced viva: questions, answers and examiner follow-ups

Practise aloud. First give a direct 20-second answer, then a derivation or evidence, then the limitation. The answer text is a preparation guide, not a script to memorise without understanding.

## Materials and physical assumptions

### 1. Why AlSi10Mg for an aircraft bracket?

It is an aluminium alloy used in additive manufacturing and offers a useful combination of low density, processability and achievable mechanical properties. Our project studies its simulated constitutive response for the existing bracket. We did not perform a comparative alloy selection or aerospace certification study, so we cannot claim it is the optimal or qualified alloy for service.

Follow-up: What evidence would selection need? Specify load spectrum, temperature, stiffness, fatigue, damage tolerance, corrosion, manufacturing route, inspection and allowables, then compare qualified material/process conditions.

### 2. Explain the role of silicon and magnesium without just naming phases.

Silicon influences solidification and the second-phase/cellular structure; magnesium supports Mg-Si precipitation strengthening under suitable processing. Obstacles to dislocation motion affect strength. The actual response depends on processing and heat treatment, which we have not characterised experimentally.

Follow-up: Can the equilibrium diagram predict an as-built LPBF microstructure? No. It provides thermodynamic context, but rapid solidification and repeated thermal cycles involve kinetics and non-equilibrium structures.

### 3. Does softening prove thermal damage or pore growth?

No. Every supplied history softens, which motivates the minus strain term, but the generator and its constitutive assumptions are unknown. Thermal recovery, damage, necking or numerical choices are possible mechanisms in general; identifying one here would require evidence absent from the project.

Follow-up: What would distinguish them? Controlled tests, local strain measurements, temperature history, microscopy and the source solver/model description.

### 4. Why is porosity not enough to predict fracture?

Mean pore fraction omits the most dangerous defect's geometry, position, orientation and surrounding microstructure. Stress concentration and crack driving force depend on those quantities. Our scalar effective-property model contains no explicit defect or crack evolution.

Follow-up: Could identical densities give different fatigue lives? Yes; a large surface-connected lack-of-fusion defect can be more damaging than many small rounded internal pores.

### 5. Is G(phi) measured? Does Voigt give a lower bound on strength loss?

D5 assumes G = 25300*(1-phi). It is the uniform-strain upper stiffness estimate for zero-stiffness pores. It is not measured, and the stiffness bound is not a rigorous theorem bounding a nonlinear bracket peak. We report an assumption-based lower estimate of sensitivity, with mesh and constitutive limitations.

Follow-up: Why keep G and density separate in the predictor? The simulation design crosses them independently, allowing partial sensitivities. Coupling them for a physical study is a separate assumption.

### 6. Why use isotropy when LPBF can be anisotropic?

The available scalar histories do not identify a full anisotropic constitutive tensor/yield surface. Isotropic J2 is a tractable wrapper assumption, not a demonstrated property of the actual print. Orientation-dependent tests would be needed to identify and validate an anisotropic model.

## Continuum mechanics and FEA

### 7. Derive von Mises stress and explain its hydrostatic insensitivity.

Define s = sigma-tr(sigma)*I/3 and sigma_eq = sqrt(3*s:s/2). Adding a hydrostatic tensor changes tr(sigma) but leaves s unchanged. Hence J2 yielding ignores mean stress. In pure shear sigma_eq = sqrt(3)*|tau|.

Follow-up: Is this sufficient for porous fracture? No. Void growth is affected by stress triaxiality, which this yield surface does not represent explicitly.

### 8. Derive the weak form rather than quoting K*u = F.

Multiply div(sigma)+b=0 by an admissible virtual displacement, integrate over the body, integrate the divergence term by parts and use the traction boundary condition. The result is equality of internal and external virtual work. Substitution of u=N*d gives element internal force Integral B^T*sigma dV; linear elasticity gives K_e = Integral B^T*C*B dV.

Follow-up: Where does nonlinearity enter? Through sigma and its history dependence, geometry if enabled, contact if present and possibly loading. Our run includes material nonlinearity with small-strain geometry; do not invent contact behaviour.

### 9. Why is a quadratic element not a guarantee of accuracy?

Interpolation order is only one part of discretisation. Geometry representation, element distortion, integration, boundary resolution and localisation also control error. A quadratic element still cannot supply the missing material length scale in an unregularised softening model.

Follow-up: What is the difference between h- and p-refinement? h reduces element size; p increases interpolation order. Our study uniformly subdivides the existing quadratic mesh.

### 10. Can the highest stress on a contour be trusted?

First inspect whether it is nodal averaged/extrapolated or integration-point/centroid data, and whether it lies at a singular support or load edge. Test its mesh behaviour and compare physically relevant spatial averages or paths. A contour maximum alone is not a converged material stress or a crack criterion.

Follow-up: Does using centroid stress remove a singularity? No. It avoids some postprocessing artefacts but does not regularise the underlying boundary idealisation.

### 11. What does ANSYS convergence establish?

That the discretised nonlinear equations satisfy the chosen iteration tolerances for that step. It does not establish mesh convergence, a correct material law or agreement with reality. Constitutive integration accuracy, global residual, discretisation and physical validation are separate checks.

Follow-up: What about a zero-error solver log? Useful execution evidence, but not proof of physical validity.

### 12. Why displacement control?

The inherited project prescribes UX = -2 mm, and the reaction is an output. Displacement control can trace some descending force branches that simple load control cannot. It does not guarantee passage through snap-back or eliminate instability/localisation.

Follow-up: Is 190 kN the applied service force? No. It is a reaction peak for this imposed displacement, mesh and material model; no service loading was established.

### 13. Why is USERMAT initially softer than the Workbench elastic run?

Its returned E is 2G*(1+nu) = 65279.06 MPa, while the Workbench elastic card uses 76600 MPa. Their ratio explains the initial bracket stiffness ratio of 0.852. The comparison changes material conditions; it cannot attribute the difference solely to the network.

Follow-up: Does Engineering Data override USERMAT's tangent? The solver uses the stiffness returned by the routine; a compatible Engineering Data elasticity entry supports setup but does not replace that return value.

### 14. What would you inspect before trusting a new ANSYS result?

Geometry and units, actual applied/active constraints, element formulation and quality, material constants and library loading, reaction equilibrium, substep convergence, state flags, energy/reaction trends and mesh/increment sensitivity of the relevant quantity. A realistic support/load model and validation data are also needed for engineering claims.

Follow-up: Did we do all possible checks? No. Report the checks in the saved evidence and identify the rest as future work.

### 15. Is small-strain analysis adequate when EQPS approaches one?

That is a serious limitation. Small-strain assumptions and total-to-plastic strain mapping are not justified by a large computed local strain. Those local values should not be presented as physically accurate. A finite-deformation model would need suitable kinematics and validation, alongside regularisation.

Follow-up: Does switching NLGEOM on solve everything? No; the material's frame, measures, mapping, calibration and localisation still need attention.

## Model mathematics and learning

### 16. Teach Equation 1 factor by factor.

The strain factor A-B*epsilon^n softens; the rate factor uses ln(rate/rate0); the thermal factor uses Tstar=(T-30)/570; G/G0 and rho/2700 give shear-modulus and porosity factors. Ratios and logarithm arguments are dimensionless. It is the user's customised form, not the classic plus-sign Johnson-Cook law.

Follow-up: Why can it not change curve shape with temperature? The non-strain factors cancel in a ratio of stresses at two strains.

### 17. Prove the backbone strain factor stays positive.

With B=A*beta/0.1^n, it becomes A*[1-beta*(epsilon/0.1)^n]. For 0<=epsilon<=0.1, n>0, A>0 and beta<=0.99, this is at least 0.01*A. This proves one factor's positivity only over its specified strain range; it is not unrestricted physical admissibility.

Follow-up: Can the temperature factor become negative? Its form is not safe for arbitrary temperature above the melt reference; we do not claim use there.

### 18. What does the neural network actually learn?

It outputs delta, a logarithmic multiplicative correction, so sigma = sigma_JC*exp(delta). The five features pass through two 16-unit tanh layers. A zero output-layer initialisation makes delta zero initially; learned weights allow condition-dependent curve shapes.

Follow-up: Is exp(delta) necessarily a small correction? No. Its initial value is one, but that is not a training constraint.

### 19. Count every parameter and explain the ensemble.

Each network has 96+272+17=385 parameters. Add seven joint equation constants: 392 per member, 1960 over five. Predictions are combined by averaging log stresses and exponentiating, which gives the geometric mean. Averaging parameters is a different operation.

Follow-up: What is the geometric mean of 100 and 144 MPa? 120 MPa, compared with an arithmetic mean of 122 MPa.

### 20. Why call this PINN with lambda = 0?

JC-PINN is the project name, but the selected implementation is best described precisely as an equation-backbone, physics-structured network. Physics penalties were candidates; selection preferred zero. It does not solve the equilibrium PDE through a residual loss and does not enforce a nonzero collocation loss.

Follow-up: Were 300-degree collocation points training evidence? No measured stresses existed there, and the selected zero penalty imposes nothing there.

### 21. Is the data loss logarithmic because the output uses an exponential?

No. The data term is squared error in normalised stress. The output parameterisation and final ensemble use logarithms/exponentials. These are distinct choices. Confusing them changes the statistical interpretation of the fit.

Follow-up: What would a log-stress loss emphasise? Approximately relative errors for small deviations, rather than the same absolute-stress weighting; that is not our selected data loss.

### 22. Why tanh, scaling, Adam and L-BFGS?

tanh supplies smooth nonlinear features and derivatives. Standardisation controls feature magnitudes using training statistics. Adam provides adaptive gradient steps, and L-BFGS uses limited-memory curvature information for subsequent optimisation. These are the recorded recipe, not a proof of a unique or global optimum.

Follow-up: What does L-BFGS reaching its iteration limit mean? It does not certify global optimality; assess fit, gradients, reproducibility and the documented stopping conditions.

### 23. What is the most important leakage risk?

Splitting points within a simulation leaks neighbouring strains and shared conditions. Cases must remain intact. Scalers and equation calibration must also be fitted inside each training fold. Earlier test exploration remains disclosed even though the final selection locks before its formal test read.

Follow-up: Are group holdouts an untouched test? No, they are part of candidate selection on the training cases.

### 24. Why does random-test error differ from unseen-group error?

The random split often retains related conditions in training. Hiding an entire temperature/rate group tests a harder task. The locked test mean is 0.439 MPa, while training-only unseen-group mean is 6.235 MPa. They evaluate different distributions and protocols.

Follow-up: Can the latter be called performance at arbitrary extrapolated temperatures? No. It concerns specific held-out groups in the supplied training design.

### 25. Does the backbone improve accuracy?

This study does not demonstrate that. Equation 1 alone has 7.37 MPa test RMSE, JC-PINN 0.439, and the same-network no-equation control 0.338. The control also has lower CV/group errors. Gains against earlier MLPs cannot isolate the backbone because training/output recipes differ.

Follow-up: Why submit JC-PINN then? The user accepted the locked equation-structured model with its disclosed trade-offs. Scientific reporting includes the unfavourable control; model changes after seeing test performance are not permitted.

### 26. What is parameter identifiability here?

Joint equation constants and the flexible correction can compensate for each other. A good overall fit does not uniquely identify physical constants. Report standalone equation calibration separately from member-specific joint constants and avoid treating the latter as measured material properties.

Follow-up: Does bounded optimisation fix non-identifiability? It limits admissible values, but does not by itself establish uniqueness or physical identification.

### 27. Does ensemble spread give a 95% confidence interval?

No. It measures disagreement between five training seeds under the same dataset and architecture. Shared bias, uncertain physics and out-of-distribution error may affect all members similarly. Calibration on appropriate independent data would be needed for coverage claims.

### 28. What does a fitted r = 0 mean?

The standalone separable law did not resolve the small density effect against its larger overall misfit. The full correction has density input and predicts a small consistent effect. A fitted exponent at a bound is not evidence that actual porosity is mechanically irrelevant.

## Constitutive integration: blackboard questions

### 29. Derive the radial-return scalar residual.

Associated J2 flow gives Delta epsilon_p = (3/2)*Delta p*s_trial/q_trial. Subtracting the elastic correction gives q_new=q_trial-3G*Delta p. Enforcing q_new=sigma_y(p_n+Delta p) yields g=q_trial-3G*Delta p-sigma_y(...)=0. Its derivative is -3G-H, so Newton adds g/(3G+H).

Follow-up: Why not 2G? The 3/2 in associated flow and 2G in deviatoric elasticity combine into 3G.

### 30. Is a positive 3G+H enough to prove the bracket is stable?

No. It concerns the local scalar return solve under this convention. Spatial localisation and global tangent stability are different issues. A well-solved constitutive update can belong to a mesh-dependent boundary-value problem.

Follow-up: Can reducing the increment fix mesh dependence? It can improve temporal/incremental integration and nonlinear convergence, but supplies no spatial length scale.

### 31. What is the consistent tangent and how would you test it?

It is the derivative of the discrete returned stress with respect to the strain increment, holding the old state fixed. Perturb each increment component from the same old state and compare finite-difference stress derivatives. Check shear conventions and branch transitions. It is needed for efficient global Newton iterations.

Follow-up: Why not perturb an already-updated state? That changes the history and no longer differentiates the intended update map.

### 32. How do you differentiate the network flow stress?

For a member, d sigma/dp=exp(delta)*(sigma_JC' + sigma_JC*delta'). Differentiate tanh with 1-tanh^2 and include the input standardisation derivative. For the geometric ensemble, sigma_hat'=sigma_hat*mean(d ln sigma_k/dp).

Follow-up: What is the derivative beyond the held strain endpoint? Zero for the flow-stress extension, by implementation choice.

### 33. Is the model really rate-dependent inside ANSYS?

Flow stress depends on a prescribed rate feature. The routine does not evolve that rate from the local plastic increment divided by the step time. It therefore does not demonstrate a general calibrated viscoplastic law under changing local rates.

Follow-up: Can a shorter static load-step time validate dynamic response? No. Inertia and an actual local rate law would need separate formulation and verification.

### 34. Is total axial strain equal to equivalent plastic strain?

Not generally. Total axial strain includes elastic strain, while equivalent plastic strain is accumulated from the plastic tensor. Their use as the same flow-curve coordinate is a project approximation because the source histories contain no resolved elastic segment. This affects physical interpretation and multiaxial transfer.

### 35. What exactly has the Fortran-to-ANSYS test verified?

The core reproduces locked flow stresses to about 2e-15 relative error offline; the single-element ANSYS stress agrees with the offline integration to 1.2e-5 MPa. These check implementation consistency for tested cases. They do not establish experimental truth or comprehensive multiaxial validation.

Follow-up: Was Abaqus tested? Its generated routine was tested offline, but Abaqus is not used. ANSYS is the project solver.

## Mesh, structural interpretation and fracture

### 36. Why does refinement lower the peak if the elastic stiffness converges?

Elastic response is comparatively well resolved. After yield, negative flow slope permits localisation without a material length scale. Refining the localisation zone changes the represented energy and response. Peak reaction drops -7.7%, despite a -0.07% stiffness change.

Follow-up: Could the load patch matter too? Yes. The hardening comparison indicates much smaller force sensitivity, but growing local strains show a separate boundary concentration contribution.

### 37. Does matching the final force prove convergence?

No. Intermediate reactions and peak force differ and max EQPS grows strongly. At -2 mm both meshes are influenced by the constant flow-stress extension beyond the data limit. The endpoint coincidence hides disagreement over the response history.

### 38. Explain crack-band regularisation from energy.

For a finite softening interval in a band of width h, dissipated energy per area scales as h times the inelastic work density. Keeping the same strain law while changing h changes that energy. A characteristic-length/energy formulation adjusts the response to a calibrated physical energy scale. Our model includes no such calibration or regularisation.

Follow-up: Is artificial numerical damping equivalent? No. It changes the problem and requires quantification; it is not a substitute for a justified spatial/physical formulation.

### 39. Can you quote 190.4 kN as bracket strength?

Only as the numerical reaction peak in the stated coarse-mesh run. It is not a converged strength, allowable or experimentally validated failure load. The peak changes with mesh, the source strain mapping is approximate, and no failure criterion was identified.

### 40. Derive critical flaw length and state why you did not compute it.

For a specified mode-I LEFM geometry, K_I=Y*sigma*sqrt(pi*a), so a_c=(K_IC/(Y*sigma))^2/pi. We lack a justified service load, flaw definition and project-specific toughness, and extensive yielding can invalidate LEFM. Substituting peak von Mises stress would not supply the proper crack-opening remote stress.

Follow-up: What replaces LEFM under large-scale yielding? An appropriate elastic-plastic fracture assessment such as J/CTOD with calibrated resistance and constraint considerations.

### 41. Why is this not a complete multiscale material model?

It links a scalar effective-material surrogate to a structural calculation. It does not explicitly solve pores, grains or dislocations or homogenise a measured microstructure. The course context is multiscale modelling, but the implemented scale linkage must be described precisely.

### 42. What is your strongest result and greatest weakness?

The strongest result is traceable numerical transfer of a locked surrogate into ANSYS, accompanied by independent verification and a mesh/control study that exposes limits. The largest structural weakness is unregularised softening and the strain mapping, while physical validation and generator provenance remain absent. A strong defence states these directly and proposes the evidence needed to improve them.

## Chain-of-question drills

Drill A: What is von Mises stress? -> Derive pure shear yielding -> Explain hydrostatic insensitivity -> Why is porous fracture pressure-sensitive? -> Why does our density factor not solve this?

Drill B: State Equation 1 -> Prove separability -> Explain the correction -> Derive parameter count -> Explain lambda = 0 -> Interpret the no-equation control -> Limit the scientific claim.

Drill C: Derive weak equilibrium -> Distinguish material and global Newton -> Derive radial return -> Define the consistent tangent -> Explain local convergence with global mesh dependence.

Drill D: Explain the reaction peak -> Compare two meshes -> Explain localisation energy -> Reject endpoint-only convergence -> Propose regularisation and its required calibration.

Drill E: Define porosity -> Explain separate versus coupled G -> Differentiate along D5 -> Distinguish stiffness bound from structural bound -> Explain why no CL follows.
