"""Material-porosity studies and comparison of supplied solver results.

No loads, elastic constants, porosity labels or lift targets are invented here.
The existing material model is unchanged. Solver imports are user-supplied
evidence, not independently validated physical predictions.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def number(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a finite number.')
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'{name} must be a finite number.') from None
    if not np.isfinite(value) or (positive and value <= 0) or (nonnegative and value < 0):
        raise ValueError(f'{name} is outside its physical domain.')
    return value


def fraction(value):
    value = number(value, 'porosity fraction', nonnegative=True)
    if value >= 1:
        raise ValueError('Porosity must satisfy 0 <= phi < 1; enter fractions, not percentages.')
    return value


def bulk_density(phi, solid_density):
    return (1 - fraction(phi)) * number(solid_density, 'solid reference density', positive=True)


def porosity_from_density(density, solid_density):
    density = number(density, 'bulk density', positive=True)
    solid_density = number(solid_density, 'solid reference density', positive=True)
    if density > solid_density:
        raise ValueError('Bulk density cannot exceed the supplied solid reference density.')
    return fraction(1 - density / solid_density)


def lift_coefficient(lift_N, air_density_kg_m3, speed_m_s, reference_area_m2):
    lift = number(lift_N, 'lift_N')  # Signed aerodynamic lift is permitted.
    rho = number(air_density_kg_m3, 'air density', positive=True)
    speed = number(speed_m_s, 'airspeed', positive=True)
    area = number(reference_area_m2, 'reference area', positive=True)
    denominator = .5 * rho * speed * speed * area
    if not np.isfinite(denominator) or denominator == 0:
        raise ValueError('Dynamic pressure times reference area must be finite and nonzero.')
    result = lift / denominator
    if not np.isfinite(result):
        raise ValueError('Lift coefficient is not finite.')
    return result


def load_config(path=None):
    return json.loads(Path(path or ROOT / 'configs/porosity_workflow.json').read_text())


def readiness(config=None):
    config = load_config() if config is None else config
    groups = {
        'porosity_mapping': ['reference_density_kg_m3', 'density_is_bulk_density', 'modulus_by_phi', 'evidence'],
        'mechanical_case': ['material_law', 'units_and_strain_definition', 'loads', 'supports', 'contacts',
                            'failure_criterion', 'evidence'],
        'aerodynamic_case': ['wing_geometry', 'operating_conditions', 'reference_area_m2',
                             'bracket_to_wing_coupling', 'evidence'],
    }
    missing = {}
    for group, keys in groups.items():
        part = config.get(group, {})
        absent = [key for key in keys if not part.get(key)]
        if group == 'porosity_mapping' and part.get('status') != 'confirmed':
            absent.insert(0, 'confirmed mapping')
        missing[group] = absent
    # Complete fields are still declarations; they do not prove a solved analysis.
    return {
        'material_model_available': (ROOT / 'runs/score/final_Svm/model_numpy.npz').exists(),
        'raw_histories_available': len(list((ROOT / 'TEAM_8_extracted_results_set_1').glob('simulation_*/STR_STR.OUT'))),
        'geometry_files': {name: (ROOT / name).exists() for name in ('Rib Bracket.STEP', 'Bracket support.STEP')},
        'missing_definitions': missing,
        'physical_completion': False,
        'note': 'Definitions and independently checked solver results are required before claiming physical completion.',
    }


def validated_mapping(mapping, *, allow_assumed=False):
    if not isinstance(mapping, dict):
        raise ValueError('Supply a mapping object with status, density, modulus pairs and evidence.')
    status = mapping.get('status')
    if status != 'confirmed' and not (status == 'assumed' and allow_assumed):
        raise ValueError('A confirmed mapping is required. An explicitly accepted assumed mapping is exploratory only.')
    if mapping.get('density_is_bulk_density') is not True:
        raise ValueError('The density-to-porosity conversion requires bulk density with negligible pore mass.')
    if not isinstance(mapping.get('evidence'), str) or not mapping['evidence'].strip():
        raise ValueError('Record the mapping source or explicit assumption rationale.')
    solid = number(mapping.get('reference_density_kg_m3'), 'solid reference density', positive=True)
    points = mapping.get('modulus_by_phi')
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError('Supply at least two phi/modulus pairs; no modulus degradation law is assumed.')
    pairs = sorted((fraction(p['phi']), number(p['G_MPa'], 'shear modulus', positive=True)) for p in points)
    if len({p for p, _ in pairs}) != len(pairs):
        raise ValueError('Each modulus mapping porosity must be unique.')
    return solid, np.array(pairs)


def material_study(mapping, phi_values, temperature_C, strain_rate_s, *, allow_assumed=False):
    from query_runtime import QueryRuntime
    from predict import warnings_for
    solid, pairs = validated_mapping(mapping, allow_assumed=allow_assumed)
    t = number(temperature_C, 'temperature')
    rate = number(strain_rate_s, 'strain rate', positive=True)
    if not isinstance(phi_values, list) or not 1 <= len(phi_values) <= 50:
        raise ValueError('Supply between 1 and 50 porosity fractions.')
    phi = np.array([fraction(v) for v in phi_values])
    if np.any(phi < pairs[0, 0]) or np.any(phi > pairs[-1, 0]):
        raise ValueError('Porosity is outside the supplied modulus mapping; extrapolation is disabled.')
    density = np.array([bulk_density(v, solid) for v in phi])
    g = np.interp(phi, pairs[:, 0], pairs[:, 1])
    x = np.column_stack([np.full(len(phi), t), np.full(len(phi), np.log10(rate)), density, g])
    # The material model itself is not validated outside its training box.
    bounds = np.array([[30, 200], [-5, -3], [2488.05, 2700], [23313.95, 25300]])
    if np.any(x < bounds[:, 0] - 1e-9) or np.any(x > bounds[:, 1] + 1e-9):
        raise ValueError('A mapped condition is outside the saved material model range. No extrapolated study was run.')
    model = QueryRuntime.load(ROOT / 'runs/score/final_Svm/model_numpy.npz')
    stress = model.predict(x)
    curves = []
    for i, value in enumerate(phi):
        curve_warnings = warnings_for(t, np.log10(rate), density[i], g[i])
        if np.any(stress[i] < 0):
            curve_warnings.append('A negative von Mises stress was predicted; this curve is unsuitable for physical interpretation.')
        curves.append({'phi': float(value), 'density_kg_m3': float(density[i]), 'G_MPa': float(g[i]),
                       'strain': model.strain.tolist(), 'stress_source_units': stress[i].tolist(),
                       'stress_at_5pct_strain': float(np.interp(.05, model.strain, stress[i])),
                       'warnings': curve_warnings})
    return {
        'kind': 'conditional_material_response',
        'mapping_status': mapping['status'], 'mapping_evidence': mapping['evidence'],
        'temperature_C': t, 'strain_rate_s': rate, 'curves': curves,
        'limitations': [
            'This is a material-curve study, not a bracket stress, strength, displacement or lift prediction.',
            'Linear interpolation is used only between the supplied phi/modulus pairs.',
            'Input units and mapping are user declarations; source stress units are still unconfirmed.',
            'A confirmed mapping does not validate the surrogate or establish physical accuracy.',
        ],
    }


STRUCTURAL_FIELDS = ('case_id', 'independent_group_id', 'geometry_sha256', 'material_definition_id',
                     'load_case_id', 'source_reference', 'comparison_group_id', 'porosity_fraction', 'temperature_C',
                     'force_x_N', 'force_y_N', 'force_z_N', 'max_displacement_mm', 'max_von_mises_MPa')
AERO_FIELDS = ('aerodynamic_condition_id', 'aerodynamic_source_reference', 'lift_N', 'air_density_kg_m3',
               'speed_m_s', 'reference_area_m2')


def read_solver_results(text):
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError('CSV must have a header with unique columns.')
    missing = set(STRUCTURAL_FIELDS) - set(reader.fieldnames)
    if missing:
        raise ValueError('Missing solver columns: ' + ', '.join(sorted(missing)))
    rows = []
    seen = set()
    for line, record in enumerate(reader, 2):
        if None in record or any(v is None for v in record.values()):
            raise ValueError(f'CSV row {line} has the wrong number of values.')
        row = dict(record)
        for key in STRUCTURAL_FIELDS[:7]:
            if not row[key].strip():
                raise ValueError(f'CSV row {line}: {key} is required.')
        if row['case_id'] in seen:
            raise ValueError('Duplicate case_id: ' + row['case_id'])
        seen.add(row['case_id'])
        digest = row['geometry_sha256']
        if len(digest) != 64 or any(c not in '0123456789abcdefABCDEF' for c in digest):
            raise ValueError('geometry_sha256 must identify the actual solved geometry file.')
        row['geometry_sha256'] = digest.lower()
        row['porosity_fraction'] = fraction(row['porosity_fraction'])
        for key in ('temperature_C', 'force_x_N', 'force_y_N', 'force_z_N'):
            row[key] = number(row[key], key)
        for key in ('max_displacement_mm', 'max_von_mises_MPa'):
            row[key] = number(row[key], key, nonnegative=True)
        has_aero = any(str(row.get(key, '')).strip() for key in AERO_FIELDS)
        row['CL'] = None
        if has_aero:
            if any(not str(row.get(key, '')).strip() for key in AERO_FIELDS):
                raise ValueError(f'CSV row {line}: supply every aerodynamic field together.')
            for key in AERO_FIELDS[2:]:
                row[key] = number(row[key], key, positive=key != 'lift_N')
            row['CL'] = lift_coefficient(*(row[key] for key in AERO_FIELDS[2:]))
        rows.append(row)
        if len(rows) > 10000:
            raise ValueError('At most 10,000 solver rows can be compared at once.')
    if not rows:
        raise ValueError('No solver results were supplied.')
    return rows


def compare_solver_results(text):
    rows = read_solver_results(text)
    groups = {}
    for row in rows:
        # Matching numerical loads/flow is required, not just matching user labels.
        key = (row['comparison_group_id'], row['geometry_sha256'], row['load_case_id'], row['temperature_C'],
               *(row[k] for k in ('force_x_N', 'force_y_N', 'force_z_N')),
               row.get('aerodynamic_condition_id', ''),
               *(row.get(k, '') for k in ('air_density_kg_m3', 'speed_m_s', 'reference_area_m2')))
        groups.setdefault(key, []).append(row)
    comparisons = []
    for group in groups.values():
        baselines = [r for r in group if r['porosity_fraction'] == 0]
        # Do not silently select among inconsistent zero-porosity runs.
        baseline = baselines[0] if len(baselines) == 1 else None
        for row in group:
            change = {}
            if baseline:
                for key in ('max_displacement_mm', 'max_von_mises_MPa', 'CL'):
                    if row[key] is not None and baseline[key] is not None:
                        change[key] = {'difference': row[key] - baseline[key],
                                       'percent': 100 * (row[key] - baseline[key]) / baseline[key]
                                       if baseline[key] != 0 else None}
            comparisons.append({**row, 'baseline_case_id': baseline['case_id'] if baseline else None,
                                'change_from_zero_porosity': change})
    return {'kind': 'supplied_solver_results', 'rows': comparisons,
            'source_csv_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'limitations': ['These are supplied solver values, not newly solved or independently validated results.',
                            'CL is calculated from supplied aerodynamic lift, air density, speed and reference area.',
                            'A baseline is used only when there is exactly one phi=0 case with matching geometry, loads and flow.',
                            'Mesh convergence, material law and structural/aerodynamic coupling must be validated separately.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    status = sub.add_parser('status')
    status.add_argument('--config', type=Path)
    study = sub.add_parser('material-study')
    study.add_argument('--config', type=Path, required=True)
    study.add_argument('--phi', nargs='+', type=float, required=True)
    study.add_argument('--temperature', type=float, required=True)
    study.add_argument('--rate', type=float, required=True)
    study.add_argument('--allow-assumed', action='store_true')
    study.add_argument('--output', type=Path, required=True)
    compare = sub.add_parser('compare-results')
    compare.add_argument('--csv', type=Path, required=True)
    compare.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    try:
        if args.command == 'status':
            result = readiness(load_config(args.config))
        elif args.command == 'material-study':
            result = material_study(load_config(args.config)['porosity_mapping'], args.phi,
                                    args.temperature, args.rate, allow_assumed=args.allow_assumed)
        else:
            result = compare_solver_results(args.csv.read_text(encoding='utf-8-sig'))
        if hasattr(args, 'output'):
            if args.output.exists():
                raise ValueError('Output exists; choose a new path to preserve previous evidence.')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    main()
