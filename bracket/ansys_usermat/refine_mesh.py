"""Uniformly refine the bracket's Workbench mesh (2 x 2 x 2 per element) for a mesh study.

No 2026 R1 Workbench is available to remesh the committed project (Workbench 2024 R1 cannot open
it), so this script refines the existing 5 mm mesh instead. Each 20-node SOLID186 element is split
into 8 children in its own parametric space: every child node is placed with the parent's
serendipity shape functions. The refined mesh therefore has
  - the same geometry as the parent mesh (the same quadratic element faces, not a new CAD fit),
  - the same element type and shapes (hexes stay hexes; SOLID186 prisms [I,J,K,K,M,N,O,O]
    give prisms of the same form where the collapsed face is, hexes elsewhere),
  - half the element size (about 2.5 mm), 8 times as many elements.
Node sets (the fixed support and the imposed-UX nodes) are carried over: a new node joins a set
when every node of the smallest parent entity it lies on (corner, edge or face) is in the set.

Input : a Workbench ds.dat (default: bracket/ansys/.../SYS-2/MECH/ds.dat, read only)
Output: OUT_DS, a ds.dat with the same commands and new nblock / eblock / CMBLOCKs.
Usage : python bracket/ansys_usermat/refine_mesh.py OUT_DS [SOURCE_DS]
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_SRC = HERE.parent / 'ansys' / 'Elastic_files' / 'dp0' / 'SYS-2' / 'MECH' / 'ds.dat'

# SOLID186 node order in parametric coordinates (xi, eta, zeta)
P = np.array([(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
              (0, -1, -1), (1, 0, -1), (0, 1, -1), (-1, 0, -1), (0, -1, 1), (1, 0, 1), (0, 1, 1), (-1, 0, 1),
              (-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], dtype=float)


def shape(x):
    """20-node serendipity shape functions at parametric points x (n, 3) -> (n, 20)."""
    x = np.atleast_2d(x)
    N = np.empty((len(x), 20))
    for k, (a, b, c) in enumerate(P):
        xi, et, ze = x[:, 0], x[:, 1], x[:, 2]
        if k < 8:
            N[:, k] = (1 + a * xi) * (1 + b * et) * (1 + c * ze) * (a * xi + b * et + c * ze - 2) / 8
        elif a == 0:
            N[:, k] = (1 - xi ** 2) * (1 + b * et) * (1 + c * ze) / 4
        elif b == 0:
            N[:, k] = (1 + a * xi) * (1 - et ** 2) * (1 + c * ze) / 4
        else:
            N[:, k] = (1 + a * xi) * (1 + b * et) * (1 - ze ** 2) / 4
    return N


def child_points():
    """Parametric positions of the 8 children's 20 nodes: (8, 20, 3)."""
    out = []
    for c in itertools.product((-0.5, 0.5), repeat=3):
        out.append(np.asarray(c) + 0.5 * P)
    # itertools order is (xi, eta, zeta) with zeta fastest; any fixed order is fine
    return np.array(out)


def parse(lines):
    i = next(k for k, l in enumerate(lines) if l.lower().startswith('nblock'))
    assert lines[i + 1].strip() == '(1i9,3e20.9e3)', lines[i + 1]
    xyz, k = {}, i + 2
    while not lines[k].startswith('-1'):
        s = lines[k]
        xyz[int(s[:9])] = [float(s[9 + 20 * j:29 + 20 * j] or 0.0) for j in range(3)]
        k += 1
    nb = (i, k)
    i = next(k for k, l in enumerate(lines) if l.lower().startswith('eblock'))
    assert 'compact' in lines[i].lower() and lines[i + 1].strip() == '(21i9)', lines[i]
    elems, k = [], i + 2
    while lines[k].strip() != '-1':
        v = [int(x) for x in lines[k].split()]
        assert len(v) == 21
        elems.append(v[1:])
        k += 1
    eb = (i, k)
    sets = {}
    for i, l in enumerate(lines):
        if l.upper().startswith('CMBLOCK') and l.split(',')[2].strip().upper() == 'NODE':
            name, n = l.split(',')[1].strip(), int(l.split(',')[3])
            vals, k = [], i + 2
            while len(vals) < n or (vals and k < len(lines) and False):
                vals += [int(lines[k][j:j + 10]) for j in range(0, len(lines[k].rstrip()), 10)]
                k += 1
            ids = []
            for v in vals:
                if v < 0:
                    ids += list(range(ids[-1] + 1, -v + 1))
                else:
                    ids.append(v)
            sets[name] = {'range': (i, k), 'ids': set(ids)}
    return xyz, nb, elems, eb, sets


# 15-node wedge (SOLID186 prism [I,J,K,K,M,N,O,O]): parametric (L1, L2, L3, zeta)
W = np.array([(1, 0, 0, -1), (0, 1, 0, -1), (0, 0, 1, -1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1),
              (.5, .5, 0, -1), (0, .5, .5, -1), (.5, 0, .5, -1), (.5, .5, 0, 1), (0, .5, .5, 1), (.5, 0, .5, 1),
              (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)], dtype=float)
# wedge node k <- SOLID186 slot: corners I J K M N O, midsides Q R T U V X, verticals Y Z A
WEDGE_FROM_186 = [0, 1, 2, 4, 5, 6, 8, 9, 11, 12, 13, 15, 16, 17, 18]
PRISM_PATTERNS = {(2, 3), (6, 7), (2, 10), (6, 14), (18, 19)}  # slots that must be equal in a prism


def wedge_shape(x):
    """15-node wedge shape functions at points x (n, 4) = (L1, L2, L3, zeta) -> (n, 15)."""
    x = np.atleast_2d(x)
    L, z = x[:, :3], x[:, 3]
    N = np.empty((len(x), 15))
    for i in range(3):
        N[:, i] = 0.5 * L[:, i] * (2 * L[:, i] - 1) * (1 - z) - 0.5 * L[:, i] * (1 - z ** 2)
        N[:, i + 3] = 0.5 * L[:, i] * (2 * L[:, i] - 1) * (1 + z) - 0.5 * L[:, i] * (1 - z ** 2)
        N[:, 12 + i] = L[:, i] * (1 - z ** 2)
    for k, (i, j) in enumerate([(0, 1), (1, 2), (2, 0)]):
        N[:, 6 + k] = 2 * L[:, i] * L[:, j] * (1 - z)
        N[:, 9 + k] = 2 * L[:, i] * L[:, j] * (1 + z)
    return N


def wedge_child_points():
    """Parametric positions of the 8 child wedges' 15 nodes: (8, 15, 4).
    The triangle splits into 4 through its edge midpoints (same orientation), times 2 layers."""
    v = np.eye(3)
    m = {(0, 1): (v[0] + v[1]) / 2, (1, 2): (v[1] + v[2]) / 2, (2, 0): (v[2] + v[0]) / 2}
    tris = [(v[0], m[0, 1], m[2, 0]), (m[0, 1], v[1], m[1, 2]), (m[2, 0], m[1, 2], v[2]), (m[0, 1], m[1, 2], m[2, 0])]
    out = []
    for z0, z1 in ((-1.0, 0.0), (0.0, 1.0)):
        zm = (z0 + z1) / 2
        for a, b, c in tris:
            corners = [a, b, c]
            pts = [(*p, z0) for p in corners] + [(*p, z1) for p in corners]
            mids = [(a + b) / 2, (b + c) / 2, (c + a) / 2]
            pts += [(*p, z0) for p in mids] + [(*p, z1) for p in mids] + [(*p, zm) for p in corners]
            out.append(pts)
    return np.array(out, dtype=float)


def wedge_to_186(w):
    """15 wedge node ids -> 20 SOLID186 prism slots [I,J,K,K,M,N,O,O, Q,R,K,T, U,V,O,X, Y,Z,A,A]."""
    return [w[0], w[1], w[2], w[2], w[3], w[4], w[5], w[5], w[6], w[7], w[2], w[8],
            w[9], w[10], w[5], w[11], w[12], w[13], w[14], w[14]]


def refine(xyz, elems, sets):
    cp = child_points()
    Nc = shape(cp.reshape(-1, 3)).reshape(8, 20, 20)
    wp = wedge_child_points()
    Nw = wedge_shape(wp.reshape(-1, 4)).reshape(8, 15, 15)
    key2id, coords, membership = {}, [], {s: set() for s in sets}
    new_elems = []

    def node_id(x):
        key = tuple(np.round(x, 5))
        if key not in key2id:
            key2id[key] = len(coords) + 1
            coords.append(x)
        return key2id[key]

    def tag(ids, params, pnodes, pparams, wedge):
        # A child node joins a set if every node of the smallest parent entity it lies on is in the set.
        # Hex: the entity is fixed by the coordinates equal to +-1. Wedge: by the area coordinates
        # equal to 0 (triangle edges/corners) and zeta = +-1 (triangle faces).
        for name, s in sets.items():
            for local, p in enumerate(params):
                if wedge:
                    fixed = [d for d in range(3) if p[d] == 0] + ([3] if abs(p[3]) == 1 else [])
                else:
                    fixed = [d for d in range(3) if abs(p[d]) == 1]
                if not fixed:
                    continue
                parent = [pnodes[k] for k in range(len(pnodes)) if all(pparams[k, d] == p[d] for d in fixed)]
                if all(n in s['ids'] for n in parent):
                    membership[name].add(ids[local])

    for nodes in elems:
        prism = all(nodes[a] == nodes[b] for a, b in PRISM_PATTERNS)
        if prism:
            wn = [nodes[k] for k in WEDGE_FROM_186]
            assert len(set(wn)) == 15, ('unexpected wedge', nodes)
            X = np.array([xyz[n] for n in wn])  # (15, 3)
            for c in range(8):
                ids = [node_id(p) for p in Nw[c] @ X]
                new_elems.append(wedge_to_186(ids))
                tag(ids, wp[c], wn, W, True)
        else:
            assert len(set(nodes)) == 20, ('unsupported degenerate element', nodes)
            X = np.array([xyz[n] for n in nodes])  # (20, 3)
            for c in range(8):
                ids = [node_id(p) for p in Nc[c] @ X]
                new_elems.append(ids)
                tag(ids, cp[c], nodes, P, False)
    return np.array(coords), new_elems, membership


def cmblock(name, ids):
    ids = sorted(ids)
    out = [f'CMBLOCK,{name},NODE,{len(ids):9d}', '(8i10)']
    for i in range(0, len(ids), 8):
        out.append(''.join(f'{v:10d}' for v in ids[i:i + 8]))
    return out


def free_faces(elems):
    """Number of element faces used once (boundary faces), by sorted corner-node keys."""
    faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    count = {}
    for e in elems:
        for f in faces:
            key = tuple(sorted(set(e[i] for i in f)))
            if len(key) >= 3:
                count[key] = count.get(key, 0) + 1
    return sum(1 for v in count.values() if v == 1)


def main():
    out = Path(sys.argv[1])
    src = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_SRC
    lines = src.read_text().split('\n')
    xyz, nb, elems, eb, sets = parse(lines)
    coords, new_elems, membership = refine(xyz, elems, sets)

    # Checks: every parent node is reproduced; the refined mesh is conforming (each parent
    # boundary face becomes 4 boundary faces); node sets keep their parent nodes.
    ids = {tuple(np.round(c, 5)) for c in coords}
    assert all(tuple(np.round(np.array(xyz[n]), 5)) in ids for e in elems for n in e), 'parent node lost'
    ff0, ff1 = free_faces(elems), free_faces(new_elems)
    assert ff1 == 4 * ff0, ('non-conforming refinement', ff0, ff1)

    attrs = next(l for l in lines[:eb[0]][::-1] if l.startswith('MAT,'))
    assert attrs.startswith('MAT,1 $ TYPE,1 $ REAL,1 $ SECNUM,1 $ ESYS,0'), attrs
    new = lines[:nb[0]]
    new += [f'nblock,3,,{len(coords)}', '(1i9,3e20.9e3)']
    new += [f'{i:9d}' + ''.join(f'{v:20.9E}' for v in c) for i, c in enumerate(coords, 1)]
    new += lines[nb[1]:eb[0]]
    new += [f'eblock,19,solid,,{len(new_elems)}     ! refine_mesh.py: 2x2x2 refinement of the Workbench mesh', '(19i9)']
    for k, e in enumerate(new_elems, 1):
        head = [1, 1, 1, 1, 0, 0, 0, 0, 20, 0, k]
        new.append(''.join(f'{v:9d}' for v in head + e[:8]))
        new.append(''.join(f'{v:9d}' for v in e[8:]))
    new.append('-1')
    rest = lines[eb[1] + 1:]
    offset = eb[1] + 1
    for name, s in sorted(sets.items(), key=lambda kv: -kv[1]['range'][0]):
        a, b = s['range'][0] - offset, s['range'][1] - offset
        rest[a:b] = cmblock(name, membership[name])
    new += rest
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(new), newline='\n')

    report = {'source': str(src), 'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
              'output': str(out), 'output_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
              'parent_elements': len(elems), 'parent_nodes': len(xyz),
              'refined_elements': len(new_elems), 'refined_nodes': len(coords),
              'parent_boundary_faces': ff0, 'refined_boundary_faces': ff1,
              'sets': {n: {'parent': len(s['ids']), 'refined': len(membership[n])} for n, s in sets.items()}}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
