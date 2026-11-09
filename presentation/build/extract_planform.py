# Mesh the z = 0 face of Rib Bracket.STEP (gmsh 4.15.2) into planform.json for diagrams.py.
# Run from the repo root: python presentation/build/extract_planform.py presentation/build/planform.json
import gmsh, json, sys
gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
import os; gmsh.model.occ.importShapes(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Rib Bracket.STEP")); gmsh.model.occ.synchronize()
gmsh.option.setNumber("Mesh.MeshSizeMax", 3.0)
gmsh.model.mesh.generate(2)
tags, coords, _ = gmsh.model.mesh.getNodes()
P = {int(t): (float(coords[3*i]), float(coords[3*i+1])) for i, t in enumerate(tags)}
et, etags, enodes = gmsh.model.mesh.getElements(2, 17)
tris = [[P[int(enodes[0][3*i+k])] for k in range(3)] for i in range(len(etags[0]))]
edges = {}
for dim, tag in gmsh.model.getBoundary([(2,17)], oriented=False):
    t0, t1 = gmsh.model.getParametrizationBounds(1, abs(tag))
    n = 60
    edges[abs(tag)] = [gmsh.model.getValue(1, abs(tag), [t0[0]+(t1[0]-t0[0])*i/n])[:2].tolist() for i in range(n+1)]
json.dump({"tris": tris, "edges": edges}, open(sys.argv[1], "w"))
print(len(tris), "triangles", len(edges), "edges")
gmsh.finalize()
