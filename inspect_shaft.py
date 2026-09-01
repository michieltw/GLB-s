import trimesh
import numpy as np

scene = trimesh.load('glb_files_modified/P02-SBT.glb')
mesh = scene.to_geometry()
if isinstance(mesh, dict):
    mesh = list(mesh.values())[0]

# filter vertices where Y > 500 (shaft area)
shaft_verts = mesh.vertices[mesh.vertices[:, 1] > 500]
print(f"Shaft vertices: {len(shaft_verts)}")
if len(shaft_verts) > 0:
    min_x, max_x = shaft_verts[:, 0].min(), shaft_verts[:, 0].max()
    min_z, max_z = shaft_verts[:, 2].min(), shaft_verts[:, 2].max()
    print(f"Shaft X width: {max_x - min_x:.2f} (from {min_x:.2f} to {max_x:.2f})")
    print(f"Shaft Z depth: {max_z - min_z:.2f} (from {min_z:.2f} to {max_z:.2f})")
