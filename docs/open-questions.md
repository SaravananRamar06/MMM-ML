# Open questions

These are the questions still open for the final JC-PINN and its use on the bracket. Each one limits a claim, but none blocks the delivered model.

| ID | Question | What it limits | What would close it |
|---|---|---|---|
| Q1 | What are the units of the data? We infer °C, s⁻¹, MPa and kg/m³ from the magnitudes. | Every stress number is "MPa (inferred)". | The instructor's solver input or documentation. |
| Q2 | Which solver and constitutive model generated the histories, and why does every one start at non-zero stress and soften? | The physical reading of Equation 1's constants. | The generator's description. |
| Q3 | Did the generator intend density as porosity? The design varies ρ and G independently. | φ = 1 − ρ/2700 is the user's definition (decision M5), not a confirmed property of the data. Density alone changes stress by only 0.34 % over φ = 0 → 7.85 % (`porosity_analysis.json`). | The instructor's design notes. |
| Q4 | What is G(φ) for the real printed bracket? | The porosity workflow needs at least two (φ, G) pairs, and `bracket/workflow/config.json` leaves them empty on purpose. G acts about 16 times more strongly than density, so this relation dominates the bracket-level porosity effect. | A measured or literature relation for LPBF AlSi10Mg. |
| Q5 | How should critical flaw length be computed: flaw geometry, LEFM or J-integral, and K_IC? | No CL prediction is made. | The project brief, plus a toughness value (about 20–30 MPa√m is reported for LPBF AlSi10Mg). |
| Q6 | What happens above 200 °C? | Curves at 300 °C are unvalidated extrapolation. No data exist there, and the selected model applies no physics penalty. | Simulations at 300 °C. |
| Q7 | Is a condition-dependent Equation 1 wanted, with B and n depending on T* and rate? | The separable form cannot change curve shape, so the correction does that work. | A user decision; a screen showed no gain from the forms tried (`improvement_screen.json`). |
| Q8 | Do the notebooks run end to end on hosted Colab and Kaggle? | Local nbclient runs pass, but hosted runs are unverified. | One run of each on the user's account. |

**Resolved, not to be asked again:**
- CL means critical flaw length.
- The data folder is complete as supplied.
- The split is a random 50/50 by case.
- The study point is φ = 4 %.
- Equation 1 and its constants are as given in the user's notes.
- The model is submitted as locked.
