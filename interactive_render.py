import bpy
import math
import random
import mathutils
import json
import os

# Global variables for user-defined parameters
USER_LIGHT_LOCATION = (0, -3, 3)
USER_LIGHT_ENERGY = 2000
USER_LIGHT_SIZE = 2
USER_LIGHT_RADIUS = 3
USER_CAMERA_DISTANCE = 4
USER_CAMERA_HEIGHT = 2
USER_FOCUS_LOCATION = None  # Will be set to center of objects if None

# Global variables for user-created objects
USER_LIGHT_OBJECT = None
USER_CAMERA_OBJECT = None

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.lights:
        bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        bpy.data.cameras.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)

def create_area_light(location=(0, -3, 3), energy=1000, size=2):
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.active_object
    light.data.energy = energy
    light.data.size = size
    return light

def get_object_center(target_obj):
    bound_box_coord_sum = mathutils.Vector()
    for bound_box_coord in target_obj.bound_box:
        bound_box_coord_sum += mathutils.Vector(bound_box_coord)

    local_obj_center = bound_box_coord_sum / len(target_obj.bound_box)
    return target_obj.matrix_world @ local_obj_center

def create_camera_with_tracking(target_objects):
    # If user camera is specified, use it
    if USER_CAMERA_OBJECT:
        camera = USER_CAMERA_OBJECT
        # Remove any existing Track To constraints
        for constraint in camera.constraints:
            if constraint.type == 'TRACK_TO':
                camera.constraints.remove(constraint)
    else:
        # Use user-defined focus location or calculate center of all target objects
        if USER_FOCUS_LOCATION is not None:
            center_point = mathutils.Vector(USER_FOCUS_LOCATION)
        else:
            centers = [get_object_center(obj) for obj in target_objects]
            center_point = sum(centers, mathutils.Vector()) / len(centers)
        
        # Create an empty to represent the center of objects
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=center_point)
        focus_empty = bpy.context.active_object
        focus_empty.name = "Focus_Empty"
        
        # Create camera at user-defined distance and height
        bpy.ops.object.camera_add(location=(USER_CAMERA_DISTANCE, 0, USER_CAMERA_HEIGHT))
        camera = bpy.context.active_object
        camera.name = "Camera"
        
        # Set as active camera
        bpy.context.scene.camera = camera
        
        # Add Track To constraint to make camera face the focus empty
        bpy.ops.object.constraint_add(type="TRACK_TO")
        track_constraint = camera.constraints["Track To"]
        track_constraint.target = focus_empty
        track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        track_constraint.up_axis = 'UP_Y'
        
        return camera, focus_empty
    
    # If using user camera, we still need a focus empty
    if USER_FOCUS_LOCATION is not None:
        center_point = mathutils.Vector(USER_FOCUS_LOCATION)
    else:
        centers = [get_object_center(obj) for obj in target_objects]
        center_point = sum(centers, mathutils.Vector()) / len(centers)
    
    # Create focus empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=center_point)
    focus_empty = bpy.context.active_object
    focus_empty.name = "Focus_Empty"
    
    # Add Track To constraint to user camera
    bpy.ops.object.constraint_add(type="TRACK_TO")
    track_constraint = camera.constraints["Track To"]
    track_constraint.target = focus_empty
    track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    track_constraint.up_axis = 'UP_Y'
    
    return camera, focus_empty

def setup_frame_export(output_dir, resolution=512, fps=30, frame_count=450):
    """Setup render settings for individual frame export"""
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = frame_count
    scene.render.filepath = os.path.join(output_dir, "frame_")
    scene.render.engine = 'BLENDER_EEVEE_NEXT'

def export_frame_info(light, frame_count, output_dir):
    """Export frame information to JSON file"""
    frame_data = {}
    
    for frame in range(1, frame_count + 1):
        # Set scene to current frame to get light properties
        bpy.context.scene.frame_set(frame)
        
        frame_name = f"frame_{frame:04d}"
        frame_data[frame_name] = {
            'light_location': tuple(light.location),
            'light_power': light.data.energy,
            'light_size': light.data.size
        }
    
    # Save to JSON file
    json_path = os.path.join(output_dir, "frame_info.json")
    with open(json_path, 'w') as f:
        json.dump(frame_data, f, indent=2)
    
    print(f"Frame information exported to: {json_path}")

def animate_light(light, center=(0,0,0), radius=3, frame_count=450):
    for frame in range(1, frame_count+1):
        angle = 2 * math.pi * (frame-1) / frame_count
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        z = center[2] + 3
        light.location = (x, y, z)
        light.keyframe_insert(data_path="location", frame=frame)

def get_selected_objects():
    """Get list of currently selected objects"""
    return [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

# User configuration functions
def set_light_parameters(location=(0, -3, 3), energy=2000, size=2, radius=3):
    """Set light parameters before rendering"""
    global USER_LIGHT_LOCATION, USER_LIGHT_ENERGY, USER_LIGHT_SIZE, USER_LIGHT_RADIUS
    USER_LIGHT_LOCATION = location
    USER_LIGHT_ENERGY = energy
    USER_LIGHT_SIZE = size
    USER_LIGHT_RADIUS = radius
    print(f"Light parameters set:")
    print(f"  Location: {location}")
    print(f"  Energy: {energy}")
    print(f"  Size: {size}")
    print(f"  Animation radius: {radius}")

def set_camera_parameters(distance=4, height=2, focus_location=None):
    """Set camera parameters before rendering"""
    global USER_CAMERA_DISTANCE, USER_CAMERA_HEIGHT, USER_FOCUS_LOCATION
    USER_CAMERA_DISTANCE = distance
    USER_CAMERA_HEIGHT = height
    USER_FOCUS_LOCATION = focus_location
    print(f"Camera parameters set:")
    print(f"  Distance: {distance}")
    print(f"  Height: {height}")
    if focus_location:
        print(f"  Focus location: {focus_location}")
    else:
        print(f"  Focus location: Auto (center of selected objects)")

def print_current_settings():
    """Print current user-defined settings"""
    print("\nCurrent Settings:")
    print(f"Light - Location: {USER_LIGHT_LOCATION}, Energy: {USER_LIGHT_ENERGY}, Size: {USER_LIGHT_SIZE}, Radius: {USER_LIGHT_RADIUS}")
    print(f"Camera - Distance: {USER_CAMERA_DISTANCE}, Height: {USER_CAMERA_HEIGHT}")
    if USER_FOCUS_LOCATION:
        print(f"Focus - Location: {USER_FOCUS_LOCATION}")
    else:
        print(f"Focus - Location: Auto (center of selected objects)")
    
    if USER_LIGHT_OBJECT:
        print(f"Using user-created light: {USER_LIGHT_OBJECT.name}")
    else:
        print("Using auto-created light")
    
    if USER_CAMERA_OBJECT:
        print(f"Using user-created camera: {USER_CAMERA_OBJECT.name}")
    else:
        print("Using auto-created camera")

def wait_for_user_setup():
    """Wait for user to set up the scene and select objects"""
    print("\nINTERACTIVE SCENE SETUP INSTRUCTIONS:")
    print("1. Import or create your objects")
    print("2. Position them as desired")
    print("3. Select all objects you want to include in the rendering")
    print("4. Optionally configure light and camera parameters:")
    print("   - set_light_parameters(location, energy, size, radius)")
    print("   - set_camera_parameters(distance, height, focus_location)")
    print("   - print_current_settings()")
    print("5. Optionally use existing lights and cameras:")
    print("   - Select a light object and call use_selected_light()")
    print("   - Select a camera object and call use_selected_camera()")
    print("   - clear_user_objects() to use auto-created objects")
    print("6. Run continue_render() when ready")
    
    # Make functions globally available
    import builtins
    builtins.continue_render = continue_render
    builtins.set_light_parameters = set_light_parameters
    builtins.set_camera_parameters = set_camera_parameters
    builtins.print_current_settings = print_current_settings
    builtins.use_selected_light = use_selected_light
    builtins.use_selected_camera = use_selected_camera
    builtins.clear_user_objects = clear_user_objects
    
    print("\nAvailable functions in Python console:")
    print("- set_light_parameters(location, energy, size, radius)")
    print("- set_camera_parameters(distance, height, focus_location)")
    print("- use_selected_light()")
    print("- use_selected_camera()")
    print("- clear_user_objects()")
    print("- print_current_settings()")
    print("- continue_render()")

def continue_render():
    """Continue with rendering after user setup"""
    # Get selected objects
    target_objects = get_selected_objects()
    
    if not target_objects:
        print("Error: No objects selected. Please select the objects you want to render.")
        return
    
    print(f"Found {len(target_objects)} selected objects. Continuing with render setup...")
    print_current_settings()
    
    # Create output directory
    output_dir = "/Users/yangmi/Documents/Projects/Blender_mesh/interact_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup scene with user-defined parameters
    if USER_LIGHT_OBJECT:
        light = USER_LIGHT_OBJECT
        print(f"Using existing light: {light.name}")
    else:
        light = create_area_light(location=USER_LIGHT_LOCATION, energy=USER_LIGHT_ENERGY, size=USER_LIGHT_SIZE)
        print("Created new light with user parameters")
    
    camera, focus_empty = create_camera_with_tracking(target_objects)
    
    # Setup for frame export
    setup_frame_export(output_dir, resolution=512, fps=30, frame_count=450)
    
    # Animate light with user-defined radius
    animate_light(light, center=(0,0,0), radius=USER_LIGHT_RADIUS, frame_count=450)
    
    # Export frame information to JSON
    export_frame_info(light, 450, output_dir)
    
    # Render individual frames
    bpy.ops.render.render(animation=True, write_still=True)
    
    print(f"Frames exported to: {output_dir}")
    print("Each frame is named: frame_0001.png, frame_0002.png, etc.")

def use_selected_light():
    """Use the currently selected light object"""
    global USER_LIGHT_OBJECT
    selected_lights = [obj for obj in bpy.context.selected_objects if obj.type == 'LIGHT']
    
    if not selected_lights:
        print("Error: No light object selected. Please select a light object.")
        return
    
    if len(selected_lights) > 1:
        print("Warning: Multiple lights selected. Using the first one.")
    
    USER_LIGHT_OBJECT = selected_lights[0]
    print(f"Using light: {USER_LIGHT_OBJECT.name}")
    print(f"Current light properties:")
    print(f"  Location: {tuple(USER_LIGHT_OBJECT.location)}")
    print(f"  Energy: {USER_LIGHT_OBJECT.data.energy}")
    print(f"  Size: {USER_LIGHT_OBJECT.data.size}")

def use_selected_camera():
    """Use the currently selected camera object"""
    global USER_CAMERA_OBJECT
    selected_cameras = [obj for obj in bpy.context.selected_objects if obj.type == 'CAMERA']
    
    if not selected_cameras:
        print("Error: No camera object selected. Please select a camera object.")
        return
    
    if len(selected_cameras) > 1:
        print("Warning: Multiple cameras selected. Using the first one.")
    
    USER_CAMERA_OBJECT = selected_cameras[0]
    bpy.context.scene.camera = USER_CAMERA_OBJECT
    print(f"Using camera: {USER_CAMERA_OBJECT.name}")
    print(f"Current camera properties:")
    print(f"  Location: {tuple(USER_CAMERA_OBJECT.location)}")
    print(f"  Rotation: {tuple(USER_CAMERA_OBJECT.rotation_euler)}")

def clear_user_objects():
    """Clear user-created object selections"""
    global USER_LIGHT_OBJECT, USER_CAMERA_OBJECT
    USER_LIGHT_OBJECT = None
    USER_CAMERA_OBJECT = None
    print("Cleared user-created object selections. Will use auto-created objects.")

def main():
    clear_scene()
    wait_for_user_setup()

if __name__ == "__main__":
    main() 