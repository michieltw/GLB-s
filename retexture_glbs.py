import os
import glob
import trimesh
import numpy as np
from PIL import Image, ImageDraw

def apply_box_mapping(mesh):
    """
    Applies Triplanar (Box) mapping to generate UVs based on vertex positions and normals.
    This avoids seams and off-center projection issues of cylindrical mapping.
    """
    # Unmerge vertices to prevent texture seams stretching across faces
    mesh.unmerge_vertices()
    vertices = mesh.vertices
    normals = mesh.vertex_normals

    uvs = np.zeros((len(vertices), 2))

    # The models are in mm. The user wants the check size to match the width of the shaft.
    # The shaft is roughly 30mm wide. We generate a 2x2 texture grid (4 squares).
    # If 1 square is 30mm, then 2 squares = 60mm.
    # Therefore, 1 full UV unit should map to 60 units of 3D spatial distance (60mm).
    scale = 60.0

    for i in range(len(vertices)):
        v = vertices[i]
        n = np.abs(normals[i])

        # Determine dominant axis for triplanar projection
        if n[0] >= n[1] and n[0] >= n[2]:
            # X is dominant: project onto YZ plane
            uvs[i] = [v[1] / scale, v[2] / scale]
        elif n[1] >= n[0] and n[1] >= n[2]:
            # Y is dominant: project onto XZ plane
            uvs[i] = [v[0] / scale, v[2] / scale]
        else:
            # Z is dominant: project onto XY plane
            uvs[i] = [v[0] / scale, v[1] / scale]

    return uvs

def process_file(in_path, out_path):
    print(f"Processing {in_path}...")
    try:
        scene = trimesh.load(in_path)

        # Create a higher-resolution checkerboard texture to avoid blurring
        # (e.g. 1024x1024 with 2x2 checks, meaning each check is 512x512)
        # This texture represents a 60mm x 60mm area (2 checks of 30mm each).
        img_size = 1024
        check_size = 512
        img = Image.new('RGB', (img_size, img_size))
        draw = ImageDraw.Draw(img)

        dark_gray = (64, 64, 64)
        almost_black = (16, 16, 16)

        for y in range(0, img_size, check_size):
            for x in range(0, img_size, check_size):
                color = dark_gray if (x // check_size + y // check_size) % 2 == 0 else almost_black
                draw.rectangle([x, y, x + check_size - 1, y + check_size - 1], fill=color)

        material = trimesh.visual.material.PBRMaterial(
            baseColorTexture=img,
            metallicFactor=0.0,
            roughnessFactor=0.8
        )

        new_scene = scene.copy()

        if hasattr(new_scene, 'geometry') and new_scene.geometry:
            for geom_name, mesh in new_scene.geometry.items():
                if not isinstance(mesh, trimesh.Trimesh):
                    continue

                # Store original faces before unmerging
                original_faces = mesh.faces.copy()

                # Apply triplanar mapping (this unmerges internally)
                new_uvs = apply_box_mapping(mesh)

                # Keep normals (which are recalculated nicely for smooth shading or flat shading based on the unmerge)
                normals = mesh.vertex_normals.copy() if hasattr(mesh, 'vertex_normals') and mesh.vertex_normals is not None else None

                new_mesh = trimesh.Trimesh(vertices=mesh.vertices,
                                           faces=mesh.faces,
                                           vertex_normals=normals,
                                           visual=trimesh.visual.TextureVisuals(uv=new_uvs))

                new_mesh.visual.material = material
                new_scene.geometry[geom_name] = new_mesh

        new_scene.export(out_path)
        print(f"Saved {out_path}")
    except Exception as e:
        print(f"Failed to process {in_path}: {e}")

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
