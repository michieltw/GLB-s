import trimesh
import numpy as np
import xatlas
from PIL import Image

# Load mesh
scene = trimesh.load('glb_files_modified/P02-SBT.glb')
mesh = scene.to_geometry()
if isinstance(mesh, dict):
    mesh = list(mesh.values())[0]

vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)

# Create a new trimesh with the unwrapped UVs
new_mesh = trimesh.Trimesh(vertices=mesh.vertices[vmapping],
                           faces=indices,
                           visual=trimesh.visual.TextureVisuals(uv=uvs))

# Calculate the scaling factor.
# The area of the 3D mesh:
area_3d = new_mesh.area
# The area of the UV map (which is in [0, 1]x[0, 1]):
# Actually let's just compute the area of the 2D triangles in UV space
v0 = uvs[indices[:, 0]]
v1 = uvs[indices[:, 1]]
v2 = uvs[indices[:, 2]]
area_2d = 0.5 * np.abs(np.cross(v1 - v0, v2 - v0))
total_area_2d = np.sum(area_2d)

print(f"3D area: {area_3d}, 2D area: {total_area_2d}")
# We want the checkerboard square to be 30mm x 30mm on the 3D mesh.
# A 2x2 pixel checkerboard image has size 2x2. One square is 1/2 of the image width.
# So the whole image covers 60mm x 60mm.
# The UV map is currently 0..1, which corresponds to some 3D area.
# If we scale the UVs so that the ratio of 3D length to UV length is 60,
# i.e., 1 UV unit = 60 mm.
# We can find a rough scale by comparing the total 3D area to the total 2D area.
# length_scale = sqrt(area_3d / total_area_2d)
# So 1 UV unit currently represents length_scale mm.
# We want 1 UV unit to represent 60 mm.
# So we should multiply the UVs by length_scale / 60.

length_scale = np.sqrt(area_3d / total_area_2d)
uv_scale = length_scale / 60.0
new_mesh.visual.uv *= uv_scale

# Create a 2x2 checkerboard image
# "dark gray & almost black"
img = Image.new('RGB', (2, 2))
pixels = img.load()
dark_gray = (64, 64, 64)
almost_black = (16, 16, 16)
pixels[0, 0] = dark_gray
pixels[1, 0] = almost_black
pixels[0, 1] = almost_black
pixels[1, 1] = dark_gray

# Create material
material = trimesh.visual.material.PBRMaterial(
    baseColorTexture=img,
    metallicFactor=0.0,
    roughnessFactor=0.8
)
new_mesh.visual.material = material

# Export to check
new_scene = trimesh.Scene(new_mesh)
new_scene.export('test_out.glb')
print("Exported test_out.glb")
