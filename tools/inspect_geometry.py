"""Inspect STEP solids with OpenCASCADE through Gmsh; no FEA is performed."""
import argparse
import hashlib
import json
from pathlib import Path


def inspect(path):
    import gmsh
    path = Path(path).resolve()
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal', 0)
        gmsh.option.setString('Geometry.OCCTargetUnit', 'MM')
        gmsh.model.add(path.stem)
        gmsh.model.occ.importShapes(str(path))
        gmsh.model.occ.synchronize()
        solids = gmsh.model.getEntities(3)
        if not solids:
            raise ValueError('No solid volumes were imported from ' + str(path))
        data = []
        for dim, tag in solids:
            faces = []
            for face_dim, face_tag in gmsh.model.getBoundary([(dim, tag)], oriented=False):
                faces.append({'tag': face_tag, 'type': gmsh.model.getType(face_dim, face_tag),
                              'area_mm2': gmsh.model.occ.getMass(face_dim, face_tag),
                              'centroid_mm': list(gmsh.model.occ.getCenterOfMass(face_dim, face_tag))})
            data.append({'tag': tag, 'volume_mm3': gmsh.model.occ.getMass(dim, tag),
                         'centroid_mm': list(gmsh.model.occ.getCenterOfMass(dim, tag)),
                         'bounding_box_mm': list(gmsh.model.getBoundingBox(dim, tag)), 'faces': faces})
        return {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'gmsh_version': gmsh.__version__, 'coordinate_unit': 'mm', 'solids': data,
                'total_volume_mm3': sum(s['volume_mm3'] for s in data),
                'limitations': ['CAD topology/measurements only; no mesh convergence or structural solve.',
                                'Face tags describe this import and must be rechecked after geometry changes.',
                                'No support, contact, load or assembly placement was inferred.']}
    finally:
        gmsh.finalize()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('files', nargs='+', type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    if args.output.exists():
        p.error('Choose a new output path; existing evidence is preserved.')
    result = {'parts': [inspect(path) for path in args.files]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({p['file']: {'volume_mm3': p['total_volume_mm3'], 'solids': len(p['solids'])}
                      for p in result['parts']}, indent=2))
