# Zone results of the corrected-load bracket runs, 18 November 2026

`zones.json` holds, for the elastic, EP and USERMAT 5 mm runs (load +P_y as UY = +2 mm on the upper half of the bore) and every saved substep, the largest tension S1, smallest S3, largest von Mises and largest plastic strain EPPL (nodal averages) in each critical zone, with the reaction.

Zones (defined in `../zone_results.py` from the STEP features):
- upper half of the bore;
- bore sides;
- the bore-fillet ligament;
- the R10 crotch fillet;
- the lower arm root and its bottom edge;
- the upper arm;
- the mounting-face corners (singular).

Every zone except the mounting-face corners stops 5 mm short of the supports.

Key values:
- **Elastic run, per kN of pin load:** R10 fillet S1 4.14 MPa/kN (highest real feature, at (31.1, 14.3) mm, mid-thickness), ligament 2.36, lower arm root 2.12, bore 1.78.
- **USERMAT run:** first plastic strain at the fillet at UY = 0.55 mm; after the peak, plastic strain grows only in the bore, ligament and fillet band (upper bore 0.186 at 2 mm).

Reproduce:

```bat
rem in a copy of each run folder holding bracket.rst
"C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ANSYS241.exe" -b -np 1 -dir . -j bracket -i dump_nodes.mac -o dump.out
python bracket\ansys_usermat\zone_results.py zones.json elastic=<elastic dump dir> ep_miso=<ep dump dir> usermat=<usermat dump dir>
```

The dump folder must sit inside the run folder, next to `bracket_history.csv`.