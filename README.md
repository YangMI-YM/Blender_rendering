# Interactive Render

## Quick start

### 1. First run the script
```bash
blender --python interactive_render.py
```

### 2. In Blender:
 - Import your models (File > Import)
 - Position them as needed
 - Select all objects you want to render

### 3. In Blender's Python console:
```python
# 1. Check what's in your scene
>>> list_mesh_objects()

All mesh objects in scene:
  - Circle: not selected
  - Cone: not selected
  - Cube: not selected

Total mesh objects: 3

# 2. Alternatively, select all mesh objects automatically
>>> select_all_mesh_objects()

# 3. Select user setup camera
>>> use_selected_camera()
Using camera: Camera
Current camera properties:
  Location: (0.6799996495246887, 4.980010986328125, 6.2000274658203125)
  Rotation: (-0.6898740530014038, 0.12217303365468979, 0.125140979886055)

# OPtionally, select user setuo light
>> user_selected_light() # detailed to be confirmed

# 4. Start rendering
>>> continue_render()
Debug - All selected objects: ['Cube', 'Cone']
Debug - Mesh objects: ['Cube', 'Cone']
Found 2 selected mesh objects: ['Cube', 'Cone']

Current Settings:
Light - Location: (0, -3, 3), Energy: 2000, Size: 2, Radius: 3
Camera - Distance: 4, Height: 2
Focus - Location: Auto (center of selected objects)
Using auto-created light
Using user-created camera: Camera
Created new light with user parameters
Warning: Failed to create Track To constraint
Frame information exported to: ./interact_output/frame_info.json
Frames exported to: ./interact_output
Each frame is named: frame_0001.png, frame_0002.png, etc.
```# Blender_rendering
