# Open items: proposals for Q4 (G(φ)) and Q5 (critical flaw length), 17 November 2026

This is a research note for the user's decisions. **Nothing here changes a result, config or document.** Every value in it is a candidate until you choose it. The numbers in the tables are illustrations, computed from the cited formulas and the saved bracket results. They are not project results.

---

## B1. Q4: shear modulus against porosity, G(φ)

**What the data already imply.** The instructor's design uses three G levels and three density levels:
- G levels: 25300, 24541 and 23313.95 MPa;
- density levels: 2700, 2619 and 2488.05 kg/m³, that is φ = 0, 3 and 7.85 %.

The G levels are **exactly G = 25300 · (1 − φ)** at those three porosities: 25300 × 0.97 = 24541, and 25300 × 0.9215 = 23313.95. This was checked against `data/manifest.json`. The design then pairs every G with every density: all 9 combinations, with 8–9 cases each. So in the data G and density vary independently, as the project has always said. The generator's G levels look as if they were made with the linear (Voigt) rule, but that rule is not stated anywhere. Any G(φ) remains an **external assumption**.

**Inputs.** The anchor is G₀ = 25300 MPa at φ = 0. The matrix Poisson ratio is ν₀ = 0.33, the project's assumed value (decision U2), which gives K₀/G₀ = 2.608. The pores are treated as isolated, roughly spherical and randomly placed. LPBF lack-of-fusion pores are often irregular, which lowers stiffness faster than these spherical-pore formulas predict.

| # | Relation | Constants (ν₀ = 0.33) | Valid for | G at φ = 0 / 4 / 7.85 % (MPa) | Inside the data's G range (23314–25300)? |
|---|---|---|---|---|---|
| 1 | **Linear (Voigt) rule**, G = G₀(1 − φ). This is the upper bound for any microstructure, and the rule the data's G levels follow. | slope −1 | any φ (bound) | 25300 / 24288 / 23314 | **yes** at all three |
| 2 | **Dewey–Mackenzie dilute** (spherical pores), G = G₀[1 + [G]φ], [G] = −15(1 − ν₀)/(7 − 5ν₀) | [G] = −1.879 | φ → 0 (dilute, roughly ≲ 10 %) | 25300 / 23399 / 21569 | no (7.85 % is below the data) |
| 3 | **Hashin–Shtrikman upper bound** for isotropic material with spherical voids, G = G₀(1 − φ)/(1 + βφ), β = 6(K₀ + 2G₀)/(9K₀ + 8G₀) | β = 0.879 | any φ, isotropic and random (bound) | 25300 / 23463 / 21810 | no |
| 4 | **Coble–Kingery quadratic**, G = G₀[1 + [G]φ + (−1 − [G])φ²], with G = 0 at φ = 1 | [G] = −1.879 | moderate φ | 25300 / 23435 / 21706 | no |
| 5 | **Spriggs exponential**, G = G₀ exp(−Bφ), with B = −[G] so that it matches row 2 at small φ. B is normally fitted to measurements. | B = 1.879 | moderate φ (violates the bound at φ → 1) | 25300 / 23469 / 21831 | no |

**Sources**
- Rows 2–5 are as summarised by W. Pabst and E. Gregorová, "Effective elastic properties of alumina-zirconia composite ceramics – Part 2. Micromechanical modeling", *Ceramics–Silikáty* 48 (1) 14–23 (2004), https://www.irsm.cas.cz/materialy/cs_content/2004/Pabst_CS_2004_0001.pdf. Its Table 1 gives [G] = −1.909 at ν₀ = 0.3 and −1.8 at 0.4. The expression above reproduces both, and gives −1.879 at 0.33.
- J. K. Mackenzie, "The elastic constants of a solid containing spherical holes", *Proc. Phys. Soc. B* 63 (1950) 2–11, doi:10.1088/0370-1301/63/1/302.
- Z. Hashin and S. Shtrikman, "A variational approach to the theory of the elastic behaviour of multiphase materials", *J. Mech. Phys. Solids* 11 (1963) 127–140, doi:10.1016/0022-5096(63)90060-7. The void-phase form in row 3 was derived from the general bound. Its slope at φ → 0, −(1 + β) = −1.879, equals Mackenzie's, which is a consistency check.
- R. L. Coble and W. D. Kingery, "Effect of porosity on physical properties of sintered alumina", *J. Am. Ceram. Soc.* 39 (1956) 377–385, doi:10.1111/j.1151-2916.1956.tb15608.x.
- R. M. Spriggs, "Expression for effect of porosity on elastic modulus of polycrystalline refractory materials, particularly aluminum oxide", *J. Am. Ceram. Soc.* 44 (1961) 628–629.

**Fit and caveats, one line each**
1. **Linear (Voigt):** the stiffest possible estimate, because real pores lower G faster than this. Its one practical advantage is that the bracket inputs stay inside the JC-PINN's data, so there is no G extrapolation and no flag 2.
2. **Dewey–Mackenzie:** the exact first-order result for small isolated spherical pores. It is the physically expected slope at low φ, but at 7.85 % it puts G about 2.3 GPa below the data's lowest G, so the model would extrapolate in G.
3. **Hashin–Shtrikman:** a rigorous upper bound for isotropic random material with spherical voids. It is close to 2 in this range, and it also leaves the data at 7.85 %.
4. **Coble–Kingery** and 5. **Spriggs:** smooth extensions of 2 with the same limitation. Spriggs's B should really be fitted to measurements.

**What was not found.** No LPBF AlSi10Mg-specific G(φ) with readable constants was found. An ultrasonic study of LPBF AlSi10Mg fitted elastic constants against micro-CT porosity with a power law ("Ultrasonic evaluation of elastic properties in laser powder bed fusion manufactured AlSi10Mg components", *NDT & E International*, 2022, https://www.sciencedirect.com/science/article/abs/pii/S0963869522001281). Its constants are behind the paywall and were not read. If you can supply that paper, its fit would be the most specific option.

A review notes that for LPBF AlSi10Mg up to about 5 % porosity, porosity correlated much more with elongation than with stiffness: https://link.springer.com/article/10.1007/s10853-022-06990-7. That suggests G changes only modestly in this range.

---

## B2. Q5: critical flaw length (CL)

**Proposed method (LEFM, mode I):** a_c = (1/π) · (K_IC / (Y·σ))².

**Which stress σ.** Use the **crack-opening (maximum principal) stress, averaged over the element centroid**, at the critical location.
- **Not the nodal peak.** Nodal peaks at the fixed-support corner are singular.
- **Not von Mises.** Von Mises does not open a crack. The saved histories (`*_history.csv`) only hold the element-centroid von Mises stress, so the maximum principal stress would need one extra post-processing pass of the saved MAPDL result files. No new solve is needed.

**At which load: the critical point.** The bracket is loaded by an imposed displacement, and no service-load magnitude exists in the project. The peak element stress of the JC-PINN bracket is 136.0 MPa (`\nBrUsermatPeakStress`, 5 mm mesh). That is the flow stress itself, so the material is yielding there.

LEFM needs small-scale yielding, meaning the plastic zone must be much smaller than the crack and the section. At σ_y ≈ 136 MPa, the Irwin plastic zone r_p = (1/2π)(K/σ_y)² is **3–31 mm** for K = 20–60 MPa√m. That is the same size as the a_c values below and as the 40 mm plate. **LEFM is therefore not valid at the peak.** This is also where the bracket results become mesh dependent (Q9).

Two options would make CL meaningful:
- **(i)** You give a service load F. Below yield the response is linear, so σ follows from the elastic run scaled to F: about 1.20 MPa per kN of reaction at the most-stressed element (1565.6 MPa at 1300.9 kN). Then use LEFM at that σ ≪ σ_y.
- **(ii)** An elastic-plastic (J-integral) method instead of LEFM. That would need a crack modelled in ANSYS, which is beyond the current scope.

**K_IC values reported for LPBF AlSi10Mg**

| Source | Condition / orientation | Value (MPa√m) | Notes |
|---|---|---|---|
| L. Hitzler, J. Hirsch, J. Schanz, B. Heine, M. Merkel, W. Hall, A. Öchsner, "Fracture toughness of selective laser melted AlSi10Mg", *Proc. IMechE Part L* 233 (4) (2019) 615–621, doi:10.1177/1464420716687337 | six build orientations, ASTM E399-08 | **40–60** | Abstract read; it reports minor directional dependence, comparable to bulk. Heat treatment not confirmed from the abstract. |
| S. AlRedha et al., "Effect of build orientation on fracture behaviour of AlSi10Mg produced by selective laser melting", *Rapid Prototyping J.* 27 (1) (2021) 112–119, doi:10.1108/RPJ-02-2020-0041 | T-S / S-T / T-L, C(T), ASTM E399-09 | **35.9 / 40.5 / 49.8** | Table 4. Not fatigue pre-cracked, so these are K_Q-type values. Heat treatment not stated. |
| Paul et al. (Gludovatz group), "Fracture resistance of AlSi10Mg fabricated by laser powder bed fusion", *Acta Materialia* 211 (2021) 116869, https://www.sciencedirect.com/science/article/abs/pii/S1359645421002494 | several scan strategies, loading directions | **≈ 20–30** (19–31) | Strongly anisotropic. The range comes from secondary summaries; the full text is paywalled and was not read. |

As-built against heat-treated values by orientation could not be tabulated from readable sources. A 2024 paper, "Fracture toughness of AlSi10Mg alloy produced by LPBF: effects of orientation and heat treatment", covers exactly that, but it was not accessible.

**Geometry factors Y, with K = Yσ√(πa)**

| Crack | Y | Source |
|---|---|---|
| Through crack at a free edge (small a/W) | 1.12 | standard edge-crack value: Tada, Paris and Irwin, *The Stress Analysis of Cracks Handbook* |
| Semicircular surface crack (a/c = 1), surface point | ≈ 0.73 | Newman and Raju, NASA TM-83200 (1981), https://ntrs.nasa.gov/citations/19810023035 |
| Semicircular surface crack (a/c = 1), deepest point | ≈ 0.66 | same |
| Embedded circular (penny) crack | 2/π ≈ 0.64 | classical result (Sneddon) |

The two Newman–Raju values were computed from the commonly quoted Newman–Raju form, Q = 1 + 1.464(a/c)^1.65 and M₁ = 1.13 − 0.09(a/c), for a small crack in a large plate. The NASA PDF timed out, so they were **not re-read from the report**. Check them before use.

**Illustration only: a_c in mm at σ = 136.0 MPa.** This is the peak element stress, where LEFM is not valid (see above).

| K (MPa√m) | Y = 1.12 | 0.73 | 0.66 | 0.64 |
|---|---|---|---|---|
| 20 (Paul, low) | 5.5 | 12.9 | 15.8 | 17.0 |
| 30 (Paul, high) | 12.3 | 29.1 | 35.6 | 38.2 |
| 35.9 (AlRedha T-S) | 17.7 | 41.6 | 50.9 | 54.7 |
| 40 (Hitzler, low) | 22.0 | 51.7 | 63.2 | 67.9 |
| 49.8 (AlRedha T-L) | 34.0 | 80.1 | 98.0 | 105.3 |
| 60 (Hitzler, high) | 49.4 | 116.3 | 142.2 | 152.9 |

Many of these values exceed the plate thickness (40 mm), and all of them are comparable to the plastic zone. That is why a service-load stress is needed.

**Limits that would carry into any CL result**
- The bracket stresses after yield are mesh dependent (Q9): halving the element size changes the peak force by −7.7 %.
- The K_IC values come from other people's specimens and processing, and there is a 2–3× spread between sources.
- There is no fracture test and no experimental validation.
- Fatigue under cyclic flight loads is not addressed by a static a_c.

---

## Your choices (Phase C starts only after these)

**(a) G(φ):**
- option 1, linear (Voigt): stays inside the data;
- option 2, Dewey–Mackenzie;
- option 3, Hashin–Shtrikman;
- option 4, Coble–Kingery;
- option 5, Spriggs (2–5 leave the data's G range at 7.85 %);
- another relation you supply (for example the LPBF ultrasonic fit, if you can provide the paper);
- **none** (Q4 stays open).

**(b) CL:**
- a **service load F** (kN) for the bracket, which is needed for a valid LEFM σ;
- a K_IC value or range from the table;
- a geometry (Y);
- the stress definition (recommended: element-centroid maximum principal stress at the hot spot);
- or **none** (Q5 stays open).
