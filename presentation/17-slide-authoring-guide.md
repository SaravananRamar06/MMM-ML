# Porosity in an additively manufactured wing-rib bracket

Canva authoring guide for Team 8. The sequence has one opening slide, 15 content slides and one closing slide. It assumes an engineering course audience familiar with stress–strain curves and basic finite-element analysis.

## Quick setup in Canva

1. Keep your existing 16:9 theme. Duplicate a content page with a clean layout and use it for the remaining slides.
2. Paste each numbered title at the top and its slide copy into a body text box. Use the visual instructions to place the graphic.
3. For each linked figure, open the PNG and copy it into Canva, or use **Uploads → Upload files**. Give plots about 60% of the slide width and keep the axes, units and legends visible.
4. Before presenting, confirm the deck has 17 pages. Use the numbered sequence below to replace any leftover template pages.

### 1. Porosity in an additively manufactured wing-rib bracket

**Slide copy**

*From AlSi10Mg stress–strain simulations to bracket response and critical flaw length*

Team 8 · Multiscale Modelling of Materials using Machine Learning

Pranav Parasuram C · R Saravanan · Dinesh Y · Amit Narayan K

**Visual.** Use the actual [bracket CAD planform](assets/cad_planform.png) on the right. Leave room for the title and presenter names on the left.

### 2. How does porosity affect the response of an AlSi10Mg wing-rib bracket?

**Slide copy**

- **Material model** · Fit JC-PINN to simulated curves.
- **Bracket response** · Compare reaction forces in ANSYS.
- **Flaw assessment** · Assess critical flaw length.

**Visual.** Center the [ready-to-paste workflow graphic with captions](assets/porosity-study-workflow-captioned.png) beneath your title. If you already placed the [unlabelled workflow graphic](assets/porosity-study-workflow.png), paste the three captions above beneath the icons instead.

### 3. The dataset contains 73 simulated material curves

**Slide copy**

- Inputs are temperature, strain rate, density, shear modulus and total axial strain.
- The target is von Mises stress sampled at 120 strain points per case.
- The case split is 36 training and 37 test. The simulated temperatures span 30–200 °C.

**Visual.** Use the [dataset curves](../figures/fig_data.png). If you crop the figure, retain the axis labels and legend. Point out that one simulation contributes a whole curve to a single split.

### 4. Johnson–Cook supplies the backbone

**Slide copy**

- The customised Equation 1 combines strain, strain rate, temperature, shear modulus and porosity.
- Density represents porosity through φ = 1 − ρ/2700.
- Equation 1 alone has a mean test curve RMSE of 7.37 MPa.

**Visual.** Typeset σ_JC = [A − Bεⁿ][1 + C ln ε̇*][1 − (T*)ᵐ][G/G₀]ᑫ[1 − φ]ʳ as a native PowerPoint equation. Use the [Equation 1 comparison](../figures/fig_eq1_fail.png) as the plot below or beside it.

### 5. A small network corrects the backbone

**Slide copy**

- Each member predicts σ = σ_JC × exp(δ).
- A 5–16–16–1 tanh network learns δ, starting at zero.
- The locked model takes the geometric mean of five members.

**Visual.** Draw two parallel paths from the same inputs to a multiplication node. Label the upper path **Equation 1** and the lower path **Neural correction exp(δ)**. Label the output **Predicted stress**. Keep the network dimensions as text instead of drawing all 385 parameters.

### 6. Model selection used the 36 training cases

**Slide copy**

- The selection score balanced case cross-validation and whole temperature–rate group holdouts equally.
- The selected model fitted the backbone constants jointly and used λ_phys = 0.
- The team locked the model before final scoring on 37 cases. Earlier project work had already explored those cases.

**Visual.** Draw **36 training cases → cross-validation and condition holdouts → lock → score 37 cases** as a four-step strip. Place the two training checks within the same box. Add **Test split previously explored** beneath the final step.

### 7. Mean test curve error was 0.439 MPa

**Slide copy**

- The 37 test curves contain 4,440 evaluated points.
- 94.9% of predictions fall within ±1 MPa.
- The highest per-case RMSE is 0.841 MPa.

**Visual.** Use the [simulated and predicted test curves](../figures/fig_test_examples.png). Put **0.439 MPa** in large type beside the plot with the caption **Mean per-case test RMSE**.

### 8. The control achieved lower error on both checks

**Slide copy**

- JC-PINN reduced mean test curve RMSE from 7.37 MPa for Equation 1 alone to 0.439 MPa.
- The same network with Equation 1 switched off scored 0.338 MPa on the test split and 5.629 MPa on condition holdouts.
- JC-PINN scored 6.235 MPa on condition holdouts. Its backbone gives the model an explicit material law.

**Visual.** Build two editable horizontal bar charts, each with its own zero-based scale and axis title. Use Equation 1, JC-PINN and the same-network control in both. Values in MPa are **7.37 / 0.439 / 0.338** for test cases and **13.95 / 6.235 / 5.629** for training-condition holdouts. Label the short bars directly.

### 9. Density alone had a small effect on simulated stress

**Slide copy**

- At matched temperature, strain rate and G, raising φ from 0% to 7.85% lowered mean simulated stress by 0.34%.
- The locked model predicts a 0.31% decrease for the same density change.

**Visual.** Use the [material porosity plot](../figures/fig_porosity.png) or make a two-bar chart labelled **Simulated histories −0.34%** and **JC-PINN −0.31%**. Put **G held fixed** directly on the chart.

### 10. The locked model runs inside ANSYS USERMAT

**Slide copy**

- The Fortran USERMAT embeds the locked model and uses a J2 return-mapping stress update.
- The constitutive mapping feeds equivalent plastic strain to a model trained on total axial strain.
- In a single-element check, MAPDL agreed with the offline result to within 1.2 × 10⁻⁵ MPa.

**Visual.** Draw **ANSYS strain increment → USERMAT stress update → stress and tangent**. Point a short vertical arrow labelled **JC-PINN flow stress** into the USERMAT box. Use the [USERMAT flowchart](../docs/ansys-flowchart/02-usermat.png) to check the sequence.

### 11. The bracket model applies an upward bore displacement

**Slide copy**

- The mounting faces are fixed.
- The upper half of the bore moves to UY = +2 mm. UX and UZ remain free there.
- The reference run uses φ = 4%, 100 °C, 10⁻⁴ s⁻¹ and G = 24,541 MPa.

**Visual.** Crop the [bore comparison](assets/bore_compact.png) to the upper-half loading example, or label the upper-half patch on the [deformation result](../bracket/ansys_usermat/workbench_2024R1/results_uy_2026-11-18/total_deformation.png). Use a single +Y arrow. Caption the load as a prescribed displacement, with service loads outside the study scope.

### 12. The JC-PINN reaction peaks and then falls

**Slide copy**

- The 5 mm reference mesh peaks at 100.5 kN at UY = 1.15 mm.
- The reaction falls to 86.3 kN at UY = 2 mm.
- Elastic and hardening elasto-plastic runs provide reference responses.

**Visual.** Use the [corrected +Y force–displacement plot](../bracket/ansys_usermat/results_uy_2026-11-18/force_displacement.png). Mark the JC-PINN peak and endpoint. Use **Reaction force** for the y-axis and **Imposed bore displacement** for the x-axis.

### 13. Coupling shear modulus to porosity increases the force change

**Slide copy**

- The coupled study assumes G = 25,300(1 − φ) MPa, a linear upper bound for stiffness.
- From φ = 0% to 7.85%, peak reaction falls 0.17% with density alone and 3.38% with G coupled.
- With G coupled, the reaction at 2 mm falls 5.12%.

**Visual.** Use the [coupled porosity force curves](../bracket/ansys_usermat/porosity_gphi_uy_2026-11-18/porosity_gphi_force_displacement.png). Add **−0.17% density-only peak change** as a small callout. Label the 4% curve **G = 24,288 MPa** so the audience can distinguish this sweep from the reference run.

### 14. Mesh refinement changes the response after yield

**Slide copy**

- Halving the element size from 5 to 2.5 mm changes initial stiffness by only −0.11%.
- The peak reaction falls from 100.5 to 90.6 kN (−9.8%).
- Plastic strain localises at the loaded bore. The post-yield reaction is mesh dependent.

**Visual.** Use the [mesh comparison plot](../bracket/ansys_usermat/mesh_uy_2026-11-18/mesh_force_displacement.png) and label the two peaks. If space permits, add the [plastic-strain contour](../bracket/ansys_usermat/contours_uy_2026-11-18/usermat_peak_eppl.png) as a small inset with its legend intact.

### 15. The crack assessment uses first yield as the load basis

**Slide copy**

- A 2D plane-strain model represents a through-thickness edge crack at the R10 fillet.
- The failure assessment diagram combines elastic crack driving force and USERMAT collapse load.
- The assessment uses a 35.9 kN capability-based load and a literature toughness band of 36–50 MPa√m.

**Visual.** On a small bracket planform, point to the R10 fillet with an annotation reading **Edge crack at R10 fillet, a = 1–30 mm**. Place a simplified two-input diagram to its right with **Elastic K_I** and **USERMAT collapse load** feeding **Failure assessment diagram**. For the oral explanation, distinguish the 35.9 kN first-yield load from the displacement-controlled peak on slide 12. The first-yield check on the 2.5 mm mesh gives about 28.5 kN.

### 16. Critical flaw length exceeds the 30 mm assessed range

**Slide copy**

- At 35.9 kN, every assessed crack up to 30 mm passes for φ = 0%, 4% and 7.85% across the chosen toughness band.
- The weakest evaluated case carries about 44.8 kN using the first collapse peak.
- At 20 MPa√m, outside the chosen band, the sensitivity check gives a critical flaw length of about 23.5 mm.

**Visual.** Use the [residual-strength curves](../bracket/ansys_usermat/crack2d_2026-11-20/residual_strength.png). Solid curves show 40 MPa√m and shading spans 36–50 MPa√m. Keep the existing **44.8 kN** annotation for **30 mm, φ = 7.85%, K_mat = 36 MPa√m**. Display **CL > 30 mm under the assessed conditions** as the headline result. The chart’s 30 mm endpoint is the largest assessed crack length.

### 17. Questions

**Slide copy**

- **Material:** 0.439 MPa mean curve RMSE on the 37 test simulations.
- **Bracket:** the assumed shear-modulus coupling gives a −3.38% peak reaction change across the porosity sweep.
- **Flaw assessment:** critical flaw length exceeds 30 mm under the assessed load and toughness band.

Footer copy: Simulation evidence only, without experimental validation. The test cases were previously explored. Units were user-confirmed without generator documentation. Temperatures above 200 °C are outside the validated range. Post-yield bracket forces depend on mesh size.

**Visual.** Keep the three takeaways as the main visual, set in three aligned rows with bold values. A faint outline of the cover CAD can serve as a background if there is sufficient contrast.

## Evidence for speaker notes

- [Generated model and bracket numbers](../report/numbers.json), [locked run](../reports/jc_pinn_20261107/README.md), [test report](../reports/jc_pinn_20261107/test_report/README.md) and [errata](../reports/jc_pinn_20261107/ERRATA.md).
- [Corrected +Y reference run](../bracket/ansys_usermat/results_uy_2026-11-18/README.md), [density-only sweep](../bracket/ansys_usermat/porosity_uy_2026-11-18/README.md), [coupled sweep](../bracket/ansys_usermat/porosity_gphi_uy_2026-11-18/README.md) and [mesh check](../bracket/ansys_usermat/mesh_uy_2026-11-18/README.md).
- [Crack model, results and sensitivity checks](../bracket/ansys_usermat/crack2d_2026-11-20/README.md) and [recorded project decisions](../docs/decisions.md).
