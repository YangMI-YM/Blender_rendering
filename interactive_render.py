import bpy
import math
import random
import mathutils
import json
import os

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
    # Calculate center of all target objects
    centers = [get_object_center(obj) for obj in target_objects]
    center_point = sum(centers, mathutils.Vector()) / len(centers)
    
    # Create an empty to represent the center of objects
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=center_point)
    focus_empty = bpy.context.active_object
    focus_empty.name = "Focus_Empty"
    
    # Create camera at a good viewing distance and height
    camera_distance = 4
    camera_height = 2
    bpy.ops.object.camera_add(location=(camera_distance, 0, camera_height))
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

def wait_for_user_setup():
    """Wait for user to set up the scene and select objects"""
    print("\nINTERACTIVE SCENE SETUP INSTRUCTIONS:")
    print("1. Import or create your objects")
    print("2. Position them as desired")
    print("3. Select all objects you want to include in the rendering")
    print("4. Run the continue_render() function when ready")
    
    # Make the continue function globally available
    import builtins
    builtins.continue_render = continue_render
    print("\nWhen ready, call continue_render() in the Python console")

def continue_render():
    """Continue with rendering after user setup"""
    # Get selected objects
    target_objects = get_selected_objects()
    
    if not target_objects:
        print("Error: No objects selected. Please select the objects you want to render.")
        return
    
    print(f"Found {len(target_objects)} selected objects. Continuing with render setup...")
    
    # Create output directory
    output_dir = "/Users/yangmi/Documents/Projects/Blender_mesh/interact_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup scene
    light = create_area_light(location=(0, -3, 3), energy=2000, size=2)
    camera, focus_empty = create_camera_with_tracking(target_objects)
    
    # Setup for frame export
    setup_frame_export(output_dir, resolution=512, fps=30, frame_count=450)
    
    # Animate light
    animate_light(light, center=(0,0,0), radius=3, frame_count=450)
    
    # Export frame information to JSON
    export_frame_info(light, 450, output_dir)
    
    # Render individual frames
    bpy.ops.render.render(animation=True, write_still=True)
    
    print(f"Frames exported to: {output_dir}")
    print("Each frame is named: frame_0001.png, frame_0002.png, etc.")

def main():
    clear_scene()
    wait_for_user_setup()

if __name__ == "__main__":
    main() 