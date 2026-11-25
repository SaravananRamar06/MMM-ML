# Whole-project flowchart

`project.svg` / `project.png` show the project in the team's order of work: (1) CAD model, (2) ANSYS Johnson–Cook material in three stages (elastic, elasto-plastic, user-defined), (3) the ML model (JC-PINN), (4) the USERMAT and its ANSYS simulation, (5) the critical flaw length (CL). `project.dot` is the editable source.

Step 5 was assessed post-hoc on 20 Nov 2026, with the locked model unchanged (decisions F1 and F2 in [decisions.md](../decisions.md)). A 2D fillet crack is modelled, K_I comes from the finite-element model, and the BS 7910 failure assessment diagram decides failure. Result: CL > 30 mm at the 35.9 kN capability-based limit load, at every porosity, for K_mat 36–50 MPa√m. This is a bound, not a value, and a static check, not fatigue. The evidence is in [crack2d_2026-11-20/](../../bracket/ansys_usermat/crack2d_2026-11-20/README.md) and [the limit-load check](../proposals/limit-load-check-2026-11-20.md).

Every figure in the chart comes from [README.md](../../README.md), [decisions.md](../decisions.md), [umat/README.md](../../umat/README.md) and, for step 5, [report/numbers.json](../../report/numbers.json). The USERMAT detail is in [../ansys-flowchart/](../ansys-flowchart/README.md).

`simple.png` / `simple.svg` / `simple.dot` is a plain-language five-step version of the same chart.

Rebuild (needs Node with `@viz-js/viz` and `sharp`, for example installed in a scratch folder and found through `NODE_PATH`):

```bash
node docs/project-flowchart/build.cjs
```

The build stops with an error if the CL numbers in either `.dot` file (limit load, largest crack, K_mat band) no longer match `report/numbers.json`.
