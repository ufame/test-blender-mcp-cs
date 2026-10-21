"""Independent round-trip verification of the delivered MDL.

Run with Blender in background mode:
  blender.exe -b --factory-startup --python verify_roundtrip.py
"""
import json
import os

import addon_utils
import bpy

MDL = r"C:\AI\goldsrc\shrek_player\models\player\shrek\shrek.mdl"
OUT = r"C:\AI\goldsrc\shrek_player\reports\final_roundtrip_delivery.json"

addon_utils.enable("bl_ext.user_default.goldsrc_model_toolchain", default_set=True)
api = bpy.app.driver_namespace["goldsrc_model_toolchain"]

result = api.import_mdl(MDL, reset_scene=True)

armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
arms = armatures[0] if armatures else None
mesh = meshes[0] if meshes else None

mesh_info = None
if mesh is not None:
    mesh_info = {
        "name": mesh.name,
        "vertices": len(mesh.data.vertices),
        "polygons": len(mesh.data.polygons),
        "triangles": sum(len(p.vertices) - 2 for p in mesh.data.polygons),
        "materials": [m.name for m in mesh.data.materials],
        "uv_layers": [uv.name for uv in mesh.data.uv_layers],
        "vertex_groups": len(mesh.vertex_groups),
        "dimensions": [round(float(v), 4) for v in mesh.dimensions],
        "location": [round(float(v), 4) for v in mesh.location],
        "scale": [round(float(v), 6) for v in mesh.scale],
        "rotation_euler_degrees": [round(float(v) * 57.29577951308232, 4) for v in mesh.rotation_euler],
    }

arm_info = None
if arms is not None:
    arm_info = {
        "name": arms.name,
        "bones": len(arms.data.bones),
        "bone_names": [b.name for b in arms.data.bones],
        "location": [round(float(v), 4) for v in arms.location],
        "scale": [round(float(v), 6) for v in arms.scale],
        "rotation_euler_degrees": [round(float(v) * 57.29577951308232, 4) for v in arms.rotation_euler],
    }

images = [
    {"name": im.name, "size": list(im.size), "packed": bool(im.packed_file)}
    for im in bpy.data.images
    if im.source == "FILE"
]

actions = []
for action in bpy.data.actions:
    start, end = action.frame_range
    actions.append({"name": action.name, "frame_start": round(float(start), 3), "frame_end": round(float(end), 3)})

payload = {
    "mdl": MDL,
    "mdl_size": os.path.getsize(MDL),
    "import_result": result,
    "armature": arm_info,
    "mesh": mesh_info,
    "actions_count": len(actions),
    "actions": actions,
    "images": images,
    "objects": [{"name": o.name, "type": o.type} for o in bpy.data.objects],
}

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, indent=2)

print("ROUNDTRIP_OK", json.dumps({
    "armature": arm_info and arm_info["name"],
    "bones": arm_info and arm_info["bones"],
    "mesh": mesh_info and mesh_info["name"],
    "vertices": mesh_info and mesh_info["vertices"],
    "triangles": mesh_info and mesh_info["triangles"],
    "actions": len(actions),
    "images": images,
}, indent=2))
