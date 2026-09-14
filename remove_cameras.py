import os
import glob
from pygltflib import GLTF2

def process_file(file_path):
    print(f"Processing {file_path}...")
    try:
        gltf = GLTF2().load(file_path)

        # Remove cameras from root
        gltf.cameras = []

        # Remove camera references from all nodes
        for node in gltf.nodes:
            if node.camera is not None:
                node.camera = None

        # Save back to the same file
        gltf.save(file_path)
        print(f"Successfully removed cameras from {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    target_dir = "glb_files_retextured_no_cameras"

    # Process all glb files in the directory
    for file_path in glob.glob(os.path.join(target_dir, "*.glb")):
        process_file(file_path)

if __name__ == "__main__":
    main()
