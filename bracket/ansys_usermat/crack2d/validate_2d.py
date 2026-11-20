import json, csv, sys
o = sys.argv[1]
def r(p):
    return [[float(v) for v in x] for x in list(csv.reader(open(p)))[1:] if x]
el = r(f'{o}/runs/elastic_a0/crack_result.csv')[0]
um = r(f'{o}/runs/usermat_gphi4_a0/crack_history.csv')
s1 = {l.split()[0]: float(l.split()[1]) for l in open(f'{o}/runs/elastic_a0/fillet_s1.txt')}
p_el = el[1] * 40 / 1e3          # kN at UY 0.1 mm
v = {'elastic_stiffness_2D_kN_per_mm': p_el / 0.1, 'elastic_stiffness_3D_kN_per_mm': 140.8,
     'usermat_phi4_initial_stiffness_2D_kN_per_mm': um[0][3] * 40 / 1e3 / um[0][2], 'usermat_phi4_stiffness_3D_kN_per_mm': 120.0,
     'usermat_phi4_peak_2D_kN': max(x[3] for x in um) * 40 / 1e3, 'usermat_phi4_peak_3D_kN': 100.5,
     'fillet_S1_2D_MPa_per_kN': s1['_S1'] / p_el, 'fillet_S1_3D_MPa_per_kN': 4.137,
     'fillet_S1_2D_location_mm': [s1['_X'], s1['_Y']], 'fillet_S1_3D_location_mm': [31.1, 14.3],
     'source_3D': 'bracket/ansys_usermat results of 18 Nov (bracket_uy, elastic_uy, zones_uy_2026-11-18/zones.json)'}
for a, b in (('elastic_stiffness_2D_kN_per_mm', 'elastic_stiffness_3D_kN_per_mm'), ('usermat_phi4_initial_stiffness_2D_kN_per_mm', 'usermat_phi4_stiffness_3D_kN_per_mm'),
             ('usermat_phi4_peak_2D_kN', 'usermat_phi4_peak_3D_kN'), ('fillet_S1_2D_MPa_per_kN', 'fillet_S1_3D_MPa_per_kN')):
    v[a.replace('_2D', '_2D_vs_3D_pct').replace('_kN_per_mm', '').replace('_MPa_per_kN', '').replace('_kN', '')] = 100 * (v[a] / v[b] - 1)
json.dump(v, open(f'{o}/validation_2d_vs_3d.json', 'w'), indent=1)
print(json.dumps(v, indent=1))
