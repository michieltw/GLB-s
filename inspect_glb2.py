import trimesh
import numpy as np

# Load a sample file
scene = trimesh.load('glb_files_modified/P02-SBT.glb')
mesh = scene.to_geometry()
# Sometimes scene is a Scene, so mesh could be a dict
if isinstance(mesh, dict):
    mesh = list(mesh.values())[0]

print("Has UVs?", hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None and len(mesh.visual.uv) > 0)
print(f"Mesh bounds: {mesh.bounds}")
