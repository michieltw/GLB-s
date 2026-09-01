# Handover Document: GLB Hockey Stick Modifications

## Overview of Findings
During the initial attempt to modify the 3D hockey stick `.glb` files, the following constraints, mesh structures, and processing techniques were discovered:

### File Structure & Orientation
- The 3D stick models are consistently oriented with their shaft running along the **Y-axis**.
- The blade is located near the origin (roughly Y = 0 or extending downward to Y = -350, depending on the model).
- The shaft typically stretches upwards.
- The geometry for each `.glb` is contained within a single `trimesh` Node/Mesh structure.

### Shaft vs Blade Separation
- The requirement is that **the blade geometry must NOT be changed**.
- A successful heuristic for identifying where the blade ends and the shaft begins is to slice the mesh horizontally (along the Y-axis) starting from the top (maximum Y) and moving downwards.
- The shaft is fairly uniform (X-range ~30, Z-range ~20). When the bounding box of a Y-slice exceeds an X-width of ~40 and a Z-width of ~30, you have reached the transition point into the blade.
- You must select a `Y_threshold` (adding a slight safety margin of e.g. +10.0 Y units) above this transition point. *Only* vertices where `Y > Y_threshold` should be mathematically stretched to elongate the stick.

### Scaling Math (Length to 1650)
- The user specified the new goal is a **Total Stick Length of 1650**.
- The total length of the original stick is `Y_max - Y_min` (which was previously observed to be roughly 600-680 depending on the model).
- To reach a total stick length of 1650 without affecting the blade, you must determine how much the shaft needs to be extended.
- The mathematical operation is to shift the vertices in the shaft dynamically:
  `new_Y = Y_threshold + (old_Y - Y_threshold) * scale_factor`
  where `scale_factor` is calculated to make the final `new_Y_max - Y_min == 1650`.

## Instructions for the Next AI Agent

1. **Branch Creation**:
   - **STOP:** Before you do anything, you must create a NEW branch in this repository to perform your work. Do not commit directly to main.

2. **Target Directory**:
   - You must exclusively process the files in the **`glb_files`** folder. (Do not process the `alle_curves` folder, as `glb_files` is the complete and canonical source). Note: You may need to ask the user to provide the `glb_files` folder if it is not currently checked into the repository yet.

3. **Elongate the Shaft (Total Length 1650)**:
   - For every `.glb` in the `glb_files` folder, write a Python script (using `trimesh` and `pygltflib`) to stretch the shaft.
   - The *total length* (from the very bottom of the blade to the top of the shaft) must equal 1650.
   - You must mathematically isolate the shaft (using the bounding-box slice heuristic described above) and strictly scale *only* the shaft. The blade must not be warped, stretched, or transformed in any way.

4. **Texture Processing (POSTPONED)**:
   - Do **NOT** attempt to apply the carbon texture map or generate procedural UV coordinates in this step.
   - The user has explicitly stated that textures will be handled in a separate, subsequent step. Only focus on elongating the shaft geometry for now.

## Required Dependencies
To run the GLB processing scripts in Python, you will need to install the following dependencies in your bash environment:
`pip install trimesh pygltflib numpy Pillow`
