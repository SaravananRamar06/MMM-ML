# Whole-project flowchart

`project.svg` / `project.png` show the project end to end: data and split, the model, training and selection on training cases only, the lock, scoring and checks, the ANSYS USERMAT and bracket work, and the documents built from saved results. `project.dot` is the editable source.

Every figure in the chart comes from [README.md](../../README.md), [decisions.md](../decisions.md) and [umat/README.md](../../umat/README.md). The USERMAT detail is in [../ansys-flowchart/](../ansys-flowchart/README.md).

`simple.png` / `simple.svg` / `simple.dot` is a plain-language eight-step version of the same chart.

Rebuild (needs Node with `@viz-js/viz` and `sharp`):

```bash
node docs/project-flowchart/build.cjs
```
