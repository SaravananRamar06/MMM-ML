# Check of the limit pin load P_L = 35.9 kN (20 November 2026)

Post-hoc check. The locked model is unchanged. Every number below is printed by `python scripts/check_limit_load.py`, which reads only committed files in `bracket/ansys_usermat/`.

## Where 35.9 kN comes from

No aircraft is defined, so no wing-loads analysis exists. The load was set as the largest limit load the bracket itself can carry (the team's hand-off notes, section 6.1):

$$P_{L,max}=\min\left(\frac{\sigma_y}{k_{vm}},\ \frac{P_{peak}}{1.5\times1.15}\right)=\min\left(\frac{136.06}{3.788},\ \frac{100.5}{1.725}\right)=\min(35.9,\ 58.3)=35.9\ \text{kN}$$

- σ_y = 136.06 MPa: the JC-PINN's initial flow stress at the study point (100 °C, 1e-4 s⁻¹, φ = 4 %), from `umat/README.md`.
- k_vm = 3.788 MPa/kN: the elastic von Mises stress per kN at the R10 fillet, 5 mm mesh, from `zones_uy_2026-11-18/zones.json`.
- 1.5 is the factor of safety (14 CFR 25.303), and 1.15 is the fitting factor (25.625).

So 35.9 kN means "the fillet just reaches yield". It is a capability bound, not a measured or specified service load.

## What was checked

| Check | Result |
|---|---|
| Arithmetic | Correct: 136.06 / 3.788 = 35.92 kN, and 100.5 / 1.725 = 58.26 kN. |
| Stress per kN | Correct for the 5 mm mesh. The fillet gives 3.788 MPa/kN von Mises and 4.137 MPa/kN S1. The support corner (3.711) is a singularity and is rightly excluded. |
| Yield stress | Correct for the study point. The USERMAT runs hold 136.06 MPa once yielded. |
| Governing criterion | First yield governs, because the capability bound (58.3 kN) is much higher. |
| **Mesh convergence** | **Not converged.** On the 2.5 mm mesh, the peak nodal stress rises from 3.788 to 4.775 MPa/kN (+26 %), which gives 136.06 / 4.775 = **28.5 kN**. The committed files do not say where that 2.5 mm peak sits, so it could be the support singularity. The USERMAT runs give the same trend: the 5 mm run has no plastic strain at 42.0 kN, but the 2.5 mm run already has plastic strain at 41.9 kN. First yield is therefore **at or below 35.9 kN**, and it falls as the mesh is refined. |
| Porosity | With G coupled (D5), first yield falls from 36.25 kN (φ = 0) to 35.82 kN (4 %) and 35.43 kN (7.85 %), a 2.3 % drop. |

## Which load the crack check should use

A crack check of an aircraft structure is a damage-tolerance residual-strength check (14 CFR 25.571(b)). The cracked part must carry **limit** load, treated as ultimate, with no extra 1.5 factor. So the right load for critical flaw length is P_L itself, not 1.5 × P_L.

| Load | kN | Status |
|---|---|---|
| Limit, 25.571(b) | 35.9 | Correct load for CL |
| Limit × 1.15 fitting factor | 41.3 | Conservative sensitivity |
| Ultimate, 1.5 × limit | 53.9 | Not the damage-tolerance load; sensitivity only |

## What this means for the CL result

- **The failure assessment's result at 35.9 kN stands.** The 2D failure assessment run on 20 Nov (committed afterwards in [`bracket/ansys_usermat/crack2d_2026-11-20/`](../../bracket/ansys_usermat/crack2d_2026-11-20/README.md)) gives CL > 30 mm at every porosity. Its weakest case is a 30 mm crack at φ = 7.85 % with K_IC = 36 MPa√m, which still carries 44.8 kN.
- **The finding holds up:**
  - 44.8 kN is above the limit load (35.9 kN) and above the limit load with the fitting factor (41.3 kN).
  - A mesh-refined limit load would be lower (about 28.5 kN), which makes CL longer, not shorter.
  - The 2D slice collapses about 12 % below the 3D model, so it is already conservative.
- **What to report:** at its own limit load, the bracket tolerates any fillet crack up to 30 mm (the crack line leaves the section at about 39 mm) at every porosity. The bracket is limited by yield, not by fracture.
- **The porosity effect** then shows up in three ways, not as one CL value:
  1. In the limit load: −2.3 % from φ 0 to 7.85 %.
  2. In the residual strength at each crack length: about −2 % at 30 mm.
  3. In CL at higher loads, from the CL-against-load curves.
- **Do not move to a different load only so that CL falls inside the modelled range.** That chooses the input from the answer.

## Limits

- **35.9 kN is a capability bound:** it applies only at the study point and depends on the mesh.
- **Service load:** no aircraft or wing-loads analysis exists, so no service load is known.
- **K_IC:** taken from the literature band of 36–50 MPa√m. No K_IC(φ) relation is known.
- **Other limits:** the 2D slice, mesh-dependent softening and the simulated data. Nothing here is experimentally validated.
