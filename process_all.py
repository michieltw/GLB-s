import os
import glob
import trimesh
import numpy as np
import xatlas
from PIL import Image

def process_file(in_path, out_path):
    print(f"Processing {in_path}...")
    scene = trimesh.load(in_path)
    mesh = scene.to_geometry()
    if isinstance(mesh, dict):
        mesh = list(mesh.values())[0]

    vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)

    new_mesh = trimesh.Trimesh(vertices=mesh.vertices[vmapping],
                               faces=indices,
                               visual=trimesh.visual.TextureVisuals(uv=uvs))

    area_3d = new_mesh.area
    v0 = uvs[indices[:, 0]]
    v1 = uvs[indices[:, 1]]
    v2 = uvs[indices[:, 2]]

    u = v1 - v0
    v = v2 - v0
    area_2d = 0.5 * np.abs(u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0])
    total_area_2d = np.sum(area_2d)

    length_scale = np.sqrt(area_3d / total_area_2d)

    # Each square is approx 30x30mm, 2x2 grid = 60x60mm
    uv_scale = length_scale / 60.0
    new_mesh.visual.uv *= uv_scale

    img = Image.new('RGB', (2, 2))
    pixels = img.load()
    dark_gray = (64, 64, 64)
    almost_black = (16, 16, 16)
    pixels[0, 0] = dark_gray
    pixels[1, 0] = almost_black
    pixels[0, 1] = almost_black
    pixels[1, 1] = dark_gray

    material = trimesh.visual.material.PBRMaterial(
        baseColorTexture=img,
        metallicFactor=0.0,
        roughnessFactor=0.8
    )
    new_mesh.visual.material = material

    new_scene = trimesh.Scene(new_mesh)
    new_scene.export(out_path)
    print(f"Saved {out_path}")

def main():
    in_dir = "glb_files_modified"
    out_dir = "glb_files_retextured"

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for in_path in glob.glob(os.path.join(in_dir, "*.glb")):
        filename = os.path.basename(in_path)
        out_path = os.path.join(out_dir, filename)
        process_file(in_path, out_path)

if __name__ == "__main__":
    main()
