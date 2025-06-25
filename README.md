# Interactive Render

## Quick start

### 1. First run the script from a terminal
```bash
blender --python interactive_render.py
# Or in my own mac, I have to do
/Applications/Blender.app/Contents/MacOS/Blender --python interactive_render.py
# You'll be able to see the following 
INTERACTIVE SCENE SETUP INSTRUCTIONS:
1. Import or create your objects
2. Position them as desired
3. Select all objects you want to include in the rendering
4. Optionally configure light and camera parameters:
   - set_light_parameters(location, energy, size, radius)
   - set_camera_parameters(distance, height, focus_location)
   - print_current_settings()
5. Optionally use existing lights and cameras:
   - Select a light object and call use_selected_light()
   - Select a camera object and call use_selected_camera()
   - clear_user_objects() to use auto-created objects
6. Run continue_render() when ready

Helper functions for object selection:
   - list_mesh_objects() - Show all mesh objects and selection status
   - select_all_mesh_objects() - Select all mesh objects automatically

Available functions in Python console:
- set_light_parameters(location, energy, size, radius)
- set_camera_parameters(distance, height, focus_location)
- use_selected_light()
- use_selected_camera()
- clear_user_objects()
- list_mesh_objects()
- select_all_mesh_objects()
- print_current_settings()
- continue_render()
```



### 2. In Blender:
 - Import your models (File > Import)
 - Position them as needed
 - Select all objects you want to render

### 3. In Blender's Python console:
```bash
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

# Optionally, select user setup light
>>> use_selected_light()
Using light: Area
Current light properties:
  Location: (5.999414920806885, -0.08377308398485184, 3.0)
  Energy: 10.0
  Size: 1.0

>>> update_current_light(energy=5000, size=3, radius=8)
Updated light 'Area':
  Location: (5.999414920806885, -0.08377308398485184, 3.0)
  Energy: 5000.0
  Size: 3.0
  Animation radius: 8

# Check everything looks right
>>> print_current_settings()
Current Settings:
Light - Location: (5.999414920806885, -0.08377308398485184, 3.0), Energy: 5000, Size: 3, Radius: 8
Camera - Distance: 4, Height: 2
Focus - Location: Auto (center of selected objects)
Using user-created light: Area
Using user-created camera: Camera

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
