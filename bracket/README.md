# Bracket: the structural side of the project

The ML model in this repository predicts the AlSi10Mg material response. This folder holds the separate structural work on the aircraft wing-rib bracket, plus two small tools that connect it to the final JC-PINN material model.

| Path | What it is |
|---|---|
| `ansys/Elastic.wbpj`, `ansys/Elastic_files/` | Your ANSYS Workbench project (static structural, elastic material). Open `Elastic.wbpj` in Workbench and keep `Elastic_files/` beside it. The files are unchanged; they were only moved here. |
| `cad/Rib Bracket.STEP`, `cad/Bracket support.STEP` | The bracket and its support, as STEP solids. |
| `geometry_report/parts_20261026.json` | Volumes, bounding boxes and face tags measured from the STEP files with OpenCASCADE/Gmsh (`tools/inspect_geometry.py`). |
| `tools/ansys_material_bridge.py` | Writes a stress–strain material card from the JC-PINN for ANSYS Engineering Data: CSV, APDL (`TB,MISO` / `TB,PLAS`) or XML. |
| `tools/inspect_geometry.py` | Re-measures the STEP files. Needs `pip install -r bracket/requirements-geometry.txt` (Gmsh). |
| `ansys_usermat/` | Runs this Workbench model in MAPDL batch with the JC-PINN USERMAT, plus elastic and EP baselines on the same mesh and load. It reads `ansys/` and does not change it. Results of 17 Nov 2026 (one mesh): `ansys_usermat/results_2026-11-17/README.md`. Porosity comparison (density only, G fixed): `ansys_usermat/porosity_2026-11-17/README.md`; with G coupled by decision D5, G = 25300 (1 − φ): `ansys_usermat/porosity_gphi_2026-11-17/README.md`. Mesh study (5 mm vs 2.5 mm; the response after yield is mesh dependent): `ansys_usermat/mesh_2026-11-17/README.md`. The same check with the hardening EP material, which shows the force dependence comes from the softening: `ansys_usermat/mesh_ep_2026-11-17/README.md`. |
| `workflow/` | A local page and CLI for porosity material studies with the JC-PINN, and for comparing bracket results exported from your solver. |

## Material card for ANSYS

```bash
python bracket/tools/ansys_material_bridge.py --temperature 100 --rate 1e-4 --density 2592 --G 24541 --format apdl --output material.mac
```

Points to keep in mind:
- The model's strain is the axial total strain `E11`. The data have no elastic segment, so plastic strain is only computed if you pass a Young's modulus you trust (`--youngs-modulus`).
- Out-of-range inputs print warnings: above 200 °C, between levels, or at 200 °C with 1e-5 /s.

## Porosity workflow

```bash
python bracket/workflow/server.py        # then open http://127.0.0.1:8767
python bracket/workflow/porosity_workflow.py material-study --phi 0 0.04 0.0785 --temperature 100 --rate 1e-4 --allow-assumed --output study.json
```

**Material study.** Porosity is converted to density with your definition φ = 1 − ρ/2700. You must supply the shear-modulus relation G(φ) as at least two φ/G pairs, because the simulations vary density and G independently and so cannot define it. The default `config.json` has that relation empty on purpose. Each predicted curve comes from the locked JC-PINN.

**Results comparison.** It reads a CSV of solved cases with these columns:
- `case_id`, `independent_group_id`, `geometry_sha256`, `material_definition_id`, `load_case_id`, `source_reference`, `comparison_group_id`;
- `porosity_fraction`, `temperature_C`, `force_x_N`, `force_y_N`, `force_z_N`, `max_displacement_mm`, `max_von_mises_MPa`.

It reports the change from the single φ = 0 case in each group that shares geometry, loads and temperature.

**What it does not do.** It solves nothing and does not predict bracket strength or critical flaw length. Imported values are your solver's, not validated here.

Tests: `tests/test_porosity_workflow.py`, `tests/test_ansys_material_bridge.py`.

## History

This folder was assembled on 7 November 2026, when the repository was rewritten around the final model.
- **Removed:** the workflow's earlier lift-coefficient path, which belonged to the withdrawn reading "CL = coefficient of lift". CL means critical flaw length.
- **Re-pointed:** the workflow's model calls, from the old query MLP to the JC-PINN.
- **Archived:** the earlier versions are on branch `archive/pre-final-2026-11-07`.
