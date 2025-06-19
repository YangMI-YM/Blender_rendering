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

def create_ground():
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    bpy.ops.object.modifier_add(type='SUBSURF')
    ground.modifiers["Subdivision"].levels = 4
    bpy.ops.object.modifier_add(type='DISPLACE')
    tex = bpy.data.textures.new('DisplaceTex', type='CLOUDS')
    ground.modifiers["Displace"].texture = tex
    bpy.ops.object.shade_smooth()
    bpy.ops.object.modifier_apply(modifier="Subdivision")
    bpy.ops.object.modifier_apply(modifier="Displace")
    return ground

def create_objects_on_ground(ground):
    # Cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-1, 0, 0))
    cube = bpy.context.active_object
    # Sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(1, 0, 0))
    sphere = bpy.context.active_object

    # Snap objects to ground
    for obj in [cube, sphere]:
        # Raycast down to find ground height
        origin = obj.location.copy()
        origin.z = 10
        direction = (0, 0, -1)
        result, location, normal, index = ground.ray_cast(origin, direction)
        if result:
            obj.location.z = location.z + obj.dimensions.z / 2
    return cube, sphere

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

def focus_camera_on_target_obj(camera_obj, target_obj):
    # Select the target object
    bpy.context.view_layer.objects.active = target_obj
    target_obj.select_set(True)
    
    # Set camera to view selected
    bpy.ops.view3d.camera_to_view_selected()
    
    # Zoom out a bit to get some space between the edge of the camera and the object
    camera_obj.location *= 1.5

def create_camera_with_tracking(cube, sphere):
    # Calculate center between cube and sphere
    cube_center = get_object_center(cube)
    sphere_center = get_object_center(sphere)
    center_point = (cube_center + sphere_center) / 2
    
    # Create an empty to represent the center of both objects
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

def setup_render(output_path, resolution=512, fps=30, frame_count=450):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = frame_count
    scene.render.filepath = output_path
    # Set render engine to EEVEE for preview
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

def animate_light(light, center=(0,0,0), radius=3, frame_count=450):
    for frame in range(1, frame_count+1):
        angle = 2 * math.pi * (frame-1) / frame_count
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        z = center[2] + 3
        light.location = (x, y, z)
        light.keyframe_insert(data_path="location", frame=frame)

def main():
    clear_scene()
    ground = create_ground()
    cube, sphere = create_objects_on_ground(ground)
    light = create_area_light(location=(0, -3, 3), energy=2000, size=2)
    camera, focus_empty = create_camera_with_tracking(cube, sphere)
    
    # Create output directory
    output_dir = "/Users/yangmi/Documents/Projects/Blender_mesh/output"
    os.makedirs(output_dir, exist_ok=True)
    
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

if __name__ == "__main__":
    main() 