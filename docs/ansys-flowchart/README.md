# JC-PINN / USERMAT / ANSYS flowcharts

Open [the offline viewer](index.html). It contains four linked, selectable-text SVG diagrams. Each also has an editable Graphviz `.dot` source and a PNG preview:

- **A — ANSYS:** global equilibrium, acceptance, load advancement, cutback and termination.
- **B — USERMAT:** wrapper checks, elastic predictor, plastic return mapping, safeguarded local iteration, error returns and material-state updates.
- **C — JC-PINN:** range flags, both strain extensions, each member's backbone and MLP correction, geometric ensemble and analytic derivative.
- **D — Plastic return mapping:** the one-time initialisation, retained bracket, Newton/midpoint updates, iteration limit and converged stress correction.

This is a diagram of the current small-strain implementation. It does not depict the bracket geometry. View A describes ANSYS control at workflow level; the actual iteration and cutback policy depends on solver settings. Views B and C describe the project routines, including their explicit checks, rather than claiming all invalid floating-point inputs are detected.

## Source of each part

- [ANSYS wrapper](../../umat/templates/ansys_usermat3d.F.in): interface requirements, temperature switch, optional elastic shear modulus, `keycut`, `erhandler`, plastic strain, energies and four state variables.
- [Solver-neutral core](../../umat/templates/jc_pinn_core.f.in): `JCPRM` (elastic trial and return mapping), `JCPFLW` (range handling) and `JCPSIG` (five-member ensemble and analytic derivative).
- [Generated ANSYS source](../../umat/jc_pinn_usermat3d.F): actual embedded model constants and weights, including numeric data-range bounds.
- [Python inference](../../src/jc_pinn.py): `equation_predict` confirms geometric averaging of member stresses.
- [Recorded decisions](../decisions.md): U1–U4 and D1–D5; [open questions](../open-questions.md): interpretation and mesh dependence.
- [ANSYS automatic time-stepping theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/ans_thry/thy_tool6.html): bisection retries from the previous converged state, subject to minimum-step controls. The saved run uses MAPDL 2024 R1; these general solver-control notes are from the 2025 R1 theory documentation.

## Important interpretation details

- The network was trained on total axial `E11`. Feeding it equivalent plastic strain is the project's stated constitutive mapping assumption.
- Strain rate is fixed as a material property. The routine does not infer it from the evolving displacement history.
- The optional positive property 7 overrides **elastic** shear modulus only; property 4 remains the network's G input.
- The lower strain extension is constant below 0.0002 and does not itself set a flag. The upper extension is constant above 0.0999 and sets bit 1. The derivative is zero strictly outside the interval; at either endpoint the model derivative is used.
- Temperature/rate/density/G are flagged, rather than input-clamped. Equation 1 separately floors its normalised temperature at zero. Bit 4 covers 200 < T ≤ 300 °C; bit 2 covers T outside 30–300 °C or rate/density/G outside their ranges, with the small numerical tolerances in the code.
- The history flag is merged from the initial evaluation and, for plastic loading, the converged final evaluation. Rejected intermediate Newton iterates are not committed as physical history.
- Local nonconvergence sets `keycut = 1`. Interface errors and core status 2–4 use ANSYS error reporting; they are not described as automatic cutback requests.
- The final selected training penalty is λ = 0. The Johnson–Cook backbone remains, with each member's own constants. Inference involves no training or physics-loss evaluation.
- Softening is unregularised and the post-yield bracket response is mesh dependent. The test was not blind; units are user-confirmed without generator documentation. Nothing is experimentally validated or validated above 200 °C. The USERMAT does not itself predict critical flaw length; the post-hoc bracket check is in [`bracket/ansys_usermat/crack2d_2026-11-20/`](../../bracket/ansys_usermat/crack2d_2026-11-20/README.md).

## Rebuild

Use Node.js with `@viz-js/viz` and `sharp` available as modules (or through `NODE_PATH`), then run:

```text
node docs/ansys-flowchart/build.cjs
```

No network request is made by the builder or viewer. Graphviz lays out explicit nodes and edges; there is no image-generation model or invented geometry. SVG remains the primary editable visual output; the `.dot` files preserve the graph structure.

## Verification

See [verification.md](verification.md) for the code cross-check, rendering inspection and repository checks performed for this addition.
