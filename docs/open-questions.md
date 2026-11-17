# Open questions

These are the questions still open for the final JC-PINN and its use on the bracket. Each one limits a claim, but none blocks the delivered model.

| ID | Question | What it limits | What would close it |
|---|---|---|---|
| Q2 | Which solver and constitutive model generated the histories, and why does every one start at non-zero stress and soften? | The physical reading of Equation 1's constants. | The generator's description. |
| Q4 | Is the assumed G(φ) close to the real printed bracket? Decision D5 adopts G = 25300 · (1 − φ), the linear (Voigt) upper bound, which the data's G levels follow exactly. | With D5, φ 0 → 7.85 % changes the bracket's peak force by −2.86 % and its force at −2 mm by −6.04 % (`bracket/ansys_usermat/porosity_gphi_2026-11-17/`), against −0.16 % for density alone. Because D5 is the stiffest possible G(φ), these values are a lower estimate; the dilute spherical-pore estimate (slope −1.88) would leave the data's G range at 7.85 %. | A measured or LPBF-specific relation (for example the ultrasonic power-law fit for LPBF AlSi10Mg, NDT & E Int. 2022) to replace the upper bound. Candidates are compared in `docs/proposals/open-items-2026-11-17.md`. |
| Q5 | How should critical flaw length be computed: flaw geometry, LEFM or J-integral, and K_IC? | No CL prediction is made. No service load exists in the project (the bracket is driven by an imposed displacement), and LEFM is not valid at the yielding peak: at σ ≈ 136 MPa (the flow stress) the plastic zone is 3–31 mm for K_IC = 20–60 MPa√m, comparable to the crack and the 40 mm plate. Reported K_IC for LPBF AlSi10Mg ranges from about 20–30 (Paul et al. 2021) through 35.9–49.8 (AlRedha et al. 2021, K_Q) to 40–60 MPa√m (Hitzler et al. 2019) (`docs/proposals/open-items-2026-11-17.md`). | A service load F from the project brief (then LEFM at the element-centroid maximum principal stress, scaled from the elastic run, with a chosen K_IC and Y), or an elastic-plastic (J-integral) crack analysis. |
| Q7 | Is a condition-dependent Equation 1 wanted, with B and n depending on T* and rate? | The separable form cannot change curve shape, so the correction does that work. | A user decision; a screen showed no gain from the forms tried (`improvement_screen.json`). |
| Q8 | Do the notebooks run end to end on hosted Colab and Kaggle? | Local nbclient runs pass, but hosted runs are unverified. | One run of each on the user's account, following `docs/hosted-notebook-check.md`. |
| Q9 | The bracket response after yield is **mesh dependent**, so how can it be made mesh independent? | The ANSYS USERMAT runs and converges on the bracket at 5 mm and 2.5 mm (`bracket/ansys_usermat/mesh_2026-11-17/`). Halving the element size changes the response:<br>- elastic stiffness: −0.07 %;<br>- peak reaction: −7.7 % (190.4 → 175.6 kN);<br>- reaction after the peak: up to −14.9 %;<br>- max element EQPS: 0.36 → 0.99, still rising.<br>The reactions meet again at −2 mm (+0.7 %) only because both settle on the flat flow stress beyond EQPS 0.0999. The strain localises next to the imposed-displacement patch. So results after yield, including the peak, are not mesh converged. With the hardening Workbench EP material, the same refinement changes the force by at most 0.3 %. The force dependence therefore comes from the softening. The peak strain at the load patch also grows with EP (×1.64, against ×2.77 for the USERMAT), so local peak strains are not mesh converged for either material (`bracket/ansys_usermat/mesh_ep_2026-11-17/`). Abaqus is not used (decision D4), so the generated Abaqus UMAT stays verified offline only. | A regularised softening law (a length scale, or a nonlocal/gradient formulation) for a mesh-independent result after yield. |

**Resolved, not to be asked again:**
- CL means critical flaw length.
- The data folder is complete as supplied.
- The split is a random 50/50 by case.
- The study point is φ = 4 %.
- Equation 1 and its constants are as given in the user's notes.
- The model is submitted as locked.
- The units are °C, s⁻¹, MPa and kg/m³ (confirmed by the user, 17 Nov 2026; was Q1).
- Density stands for porosity, φ = 1 − ρ/2700 (confirmed by the user, 17 Nov 2026; was Q3).
- The ANSYS USERMAT builds and runs on the user's MAPDL 2024 R1. It was built with ifx 2026.2 and VS 2019, and the single-element test passes to 1.2×10⁻⁵ MPa (17 Nov 2026; was Q10).
- No simulations above 200 °C will be added. 200–300 °C stays unvalidated extrapolation and is flagged (user, 17 Nov 2026; was Q6).
