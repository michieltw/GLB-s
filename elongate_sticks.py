import os
import glob
import pygltflib
import trimesh
import numpy as np
import struct
import base64

def process_file(filepath, outpath):
    print(f"Processing {filepath}...")
    try:
        gltf = pygltflib.GLTF2().load(filepath)
    except Exception as e:
        print(f"  Error loading {filepath}: {e}")
        return False

    target_length = 1650.0
    modified = False

    for mesh_idx, mesh in enumerate(gltf.meshes):
        for prim_idx, primitive in enumerate(mesh.primitives):
            pos_accessor_idx = primitive.attributes.POSITION
            if pos_accessor_idx is None:
                continue

            pos_accessor = gltf.accessors[pos_accessor_idx]
            pos_buffer_view = gltf.bufferViews[pos_accessor.bufferView]
            pos_buffer = gltf.buffers[pos_buffer_view.buffer]
            data = bytearray(gltf.get_data_from_buffer_uri(pos_buffer.uri))

            pos_offset = pos_buffer_view.byteOffset + (pos_accessor.byteOffset or 0)
            pos_stride = pos_buffer_view.byteStride or 12
            count = pos_accessor.count

            vertices = []
            for i in range(count):
                idx = pos_offset + i * pos_stride
                v = struct.unpack('<fff', data[idx:idx+12])
                vertices.append(list(v))
            vertices = np.array(vertices)

            y_min = vertices[:, 1].min()
            y_max = vertices[:, 1].max()

            # Find transition
            slice_height = 5.0
            transition_y = None

            for y in np.arange(y_max, y_min, -slice_height):
                slice_verts = vertices[(vertices[:, 1] >= y - slice_height) & (vertices[:, 1] <= y)]
                if len(slice_verts) == 0: continue
                x_width = slice_verts[:, 0].max() - slice_verts[:, 0].min()
                z_width = slice_verts[:, 2].max() - slice_verts[:, 2].min()
                if x_width > 40 or z_width > 30:
                    transition_y = y
                    break

            if transition_y is None:
                print(f"  Warning: No transition found for {filepath} (Mesh {mesh_idx}, Prim {prim_idx})")
                continue

            y_threshold = transition_y + 10.0
            current_shaft_length = y_max - y_threshold
            new_y_max = y_min + target_length
            target_shaft_length = new_y_max - y_threshold

            if current_shaft_length <= 0:
                print(f"  Warning: current_shaft_length <= 0 for {filepath} (Mesh {mesh_idx}, Prim {prim_idx})")
                continue

            scale_factor = target_shaft_length / current_shaft_length

            # Scale vertices
            mask = vertices[:, 1] > y_threshold
            vertices[mask, 1] = y_threshold + (vertices[mask, 1] - y_threshold) * scale_factor

            # Write back positions
            for i in range(count):
                idx = pos_offset + i * pos_stride
                struct.pack_into('<fff', data, idx, *vertices[i])

            pos_accessor.min = vertices.min(axis=0).tolist()
            pos_accessor.max = vertices.max(axis=0).tolist()

            # Recalculate normals if indices are available
            if primitive.indices is not None:
                idx_accessor_idx = primitive.indices
                idx_accessor = gltf.accessors[idx_accessor_idx]
                idx_buffer_view = gltf.bufferViews[idx_accessor.bufferView]
                idx_offset = idx_buffer_view.byteOffset + (idx_accessor.byteOffset or 0)

                if idx_accessor.componentType == pygltflib.UNSIGNED_SHORT:
                    fmt = '<H'
                    size = 2
                elif idx_accessor.componentType == pygltflib.UNSIGNED_INT:
                    fmt = '<I'
                    size = 4
                elif idx_accessor.componentType == pygltflib.UNSIGNED_BYTE:
                    fmt = '<B'
                    size = 1
                else:
                    print(f"  Warning: Unsupported index type {idx_accessor.componentType} in {filepath}")
                    fmt = None

                if fmt is not None:
                    faces = []
                    for i in range(idx_accessor.count // 3):
                        face = []
                        for j in range(3):
                            idx = idx_offset + (i * 3 + j) * size
                            face.append(struct.unpack(fmt, data[idx:idx+size])[0])
                        faces.append(face)

                    tmesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
                    new_normals = tmesh.vertex_normals

                    if hasattr(primitive.attributes, 'NORMAL') and primitive.attributes.NORMAL is not None:
                        norm_accessor_idx = primitive.attributes.NORMAL
                        norm_accessor = gltf.accessors[norm_accessor_idx]
                        norm_buffer_view = gltf.bufferViews[norm_accessor.bufferView]
                        norm_offset = norm_buffer_view.byteOffset + (norm_accessor.byteOffset or 0)
                        norm_stride = norm_buffer_view.byteStride or 12

                        for i in range(count):
                            idx = norm_offset + i * norm_stride
                            struct.pack_into('<fff', data, idx, *new_normals[i])

            pos_buffer.uri = "data:application/octet-stream;base64," + base64.b64encode(data).decode('utf-8')
            modified = True

    if modified:
        try:
            gltf.save(outpath)
            return True
        except Exception as e:
            print(f"  Error saving {outpath}: {e}")
            return False
    else:
        print(f"  No modifications made to {filepath}")
        return False

def main():
    if not os.path.exists("glb_files_modified"):
        os.makedirs("glb_files_modified")

    files = glob.glob("glb_files/*.glb")
    success_count = 0
    fail_count = 0

    for filepath in files:
        filename = os.path.basename(filepath)
        outpath = os.path.join("glb_files_modified", filename)
        if process_file(filepath, outpath):
            success_count += 1
        else:
            fail_count += 1

    print(f"\nProcessing complete. Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    main()
