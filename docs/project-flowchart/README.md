# Whole-project flowchart

`project.svg` / `project.png` show the project in the team's order of work: (1) CAD model, (2) ANSYS Johnson–Cook material in three stages (elastic, elasto-plastic, user-defined), (3) the ML model (JC-PINN), (4) the USERMAT and its ANSYS simulation, (5) prediction of the critical length. Step 5 is drawn as planned and not done: the repository has no flaw or toughness data, and the method is still to be decided. `project.dot` is the editable source.

Every figure in the chart comes from [README.md](../../README.md), [decisions.md](../decisions.md) and [umat/README.md](../../umat/README.md). The USERMAT detail is in [../ansys-flowchart/](../ansys-flowchart/README.md).

`simple.png` / `simple.svg` / `simple.dot` is a plain-language five-step version of the same chart.

Rebuild (needs Node with `@viz-js/viz` and `sharp`):

```bash
node docs/project-flowchart/build.cjs
```
