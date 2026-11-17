# Open questions

These are the questions still open for the final JC-PINN and its use on the bracket. Each one limits a claim, but none blocks the delivered model.

| ID | Question | What it limits | What would close it |
|---|---|---|---|
| Q2 | Which solver and constitutive model generated the histories, and why does every one start at non-zero stress and soften? | The physical reading of Equation 1's constants. | The generator's description. |
| Q4 | What is G(φ) for the real printed bracket? | The porosity workflow needs at least two (φ, G) pairs, and `bracket/workflow/config.json` leaves them empty on purpose. G acts about 16 times more strongly than density, so this relation dominates the bracket-level porosity effect. | A measured or literature relation for LPBF AlSi10Mg. |
| Q5 | How should critical flaw length be computed: flaw geometry, LEFM or J-integral, and K_IC? | No CL prediction is made. | The project brief, plus a toughness value (about 20–30 MPa√m is reported for LPBF AlSi10Mg). |
| Q7 | Is a condition-dependent Equation 1 wanted, with B and n depending on T* and rate? | The separable form cannot change curve shape, so the correction does that work. | A user decision; a screen showed no gain from the forms tried (`improvement_screen.json`). |
| Q8 | Do the notebooks run end to end on hosted Colab and Kaggle? | Local nbclient runs pass, but hosted runs are unverified. | One run of each on the user's account. |
| Q9 | The bracket response after yield is **mesh dependent**, so how can it be made mesh independent? (Also: do the UMAT and USERMAT run in Abaqus?) | The ANSYS USERMAT runs and converges on the bracket at 5 mm and 2.5 mm (`bracket/ansys_usermat/mesh_2026-11-17/`). Halving the element size changes the response:<br>- elastic stiffness: −0.07 %;<br>- peak reaction: −7.7 % (190.4 → 175.6 kN);<br>- reaction after the peak: up to −14.9 %;<br>- max element EQPS: 0.36 → 0.99, still rising.<br>The reactions meet again at −2 mm (+0.7 %) only because both settle on the flat flow stress beyond EQPS 0.0999. The strain localises next to the imposed-displacement patch. So results after yield, including the peak, are not mesh converged. The Abaqus UMAT has been checked only offline. | A regularised softening law (a length scale, or a nonlocal/gradient formulation) for a mesh-independent result after yield. A hardening-material run on the fine mesh to separate softening from the load-patch concentration. One Abaqus single-element job, then an Abaqus bracket run. |

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
