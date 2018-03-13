"""
output file format:
    - object keyframe row:
        object_id, frame,
        location_0, location_1, location_2,
        rotation_euler_0, rotation_euler_1, rotation_euler_2,
        sale_0, scale_1, scale_2

    - material keyframe row:
        object_id, frame,
        diffuse_color_r, diffuse_color_g, diffuse_color_b,
        specular_color_r ,specular_color_g, specular_color_b,
        emit, ambient, translucency
"""

import re
import bpy

bl_info = {
    "name": "save object keyframes",
    "author": "Drunkar",
    "version": (0, 5),
    "blender": (2, 7, 9),
    "location": "View3D > Object > Animation > SaveKeyframes, Ctrl + Alt + k",
    "description": "Save keyframes of object, which matched a keyword.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


addon_keymaps = []


class SaveKeyframes(bpy.types.Operator):

    bl_idname = "object.save_object_keyframes"
    bl_label = "save object keyframes"
    bl_description = "Save keyframes of object, which matched a keyword."
    bl_options = {"REGISTER", "UNDO"}

    # main
    def execute(self, context):
        keyframe_index = {"location": 0, "rotation_euler": 3, "scale": 6}
        objs = []
        for name, obj in bpy.context.scene.objects.items():
            matched = re.search(context.scene.save_keyframes_id_key, name)
            if matched:
                objs.append(obj)

        keyframes = {}
        start_frame = context.scene.save_keyframes_start_frame
        end_frame = context.scene.save_keyframes_end_frame
        for obj in objs:

            # extract keyframes
            # [[keyframe_index, frame, value], [], ...]
            kfs = []
            for fc in obj.animation_data.action.fcurves:
                if fc.data_path.endswith(("location", "rotation_euler", "scale")):
                    kfs += [[keyframe_index[fc.data_path] + fc.array_index, i.co[0], i.co[1]]
                            for i in fc.keyframe_points
                            if i.co[0] >= start_frame and i.co[0] <= end_frame]

            # register keyframes
            # {obj_name: {
            #     frame_1: [
            #               location_0,location_1,location_2,
            #               rotation_euler_0,rotation_euler_1,rotation_euler_2,
            #               sale_0,scale_1,scale_2
            #              ],
            #     frame_2: [], ...}
            keyframes[obj.name] = {}
            for key in kfs:
                fr = str(int(key[1]))
                if fr in keyframes[obj.name]:
                    keyframes[obj.name][fr][key[0]] = key[2]
                else:
                    keyframes[obj.name][fr] = [
                        0, 0, 0, 0, 0, 0, 1, 1, 1]
                    keyframes[obj.name][fr][key[0]] = key[2]

        if bpy.data.is_saved:
            filepath = bpy.path.abspath(
                "//" + context.scene.save_keyframes_file_name + ".csv")
            with open(filepath, "w") as f:
                for uav, frames in keyframes.items():
                    for frame, v in frames.items():
                        v = map(str, v)
                        f.write(uav + "," + frame + "," + ",".join(v) + "\n")
        else:
            raise Exception("Please save blender file first.")
        return {"FINISHED"}

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene, "save_keyframes_id_key")
        col.prop(context.scene, "save_keyframes_start_frame")
        col.prop(context.scene, "save_keyframes_end_frame")
        col.prop(context.scene, "save_keyframes_file_name")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SaveMaterialKeyframes(bpy.types.Operator):

    bl_idname = "object.save_object_material_keyframes"
    bl_label = "save object material keyframes"
    bl_description = "Save keyframes of object\'s material, which matched a keyword."
    bl_options = {"REGISTER", "UNDO"}

    # main
    def execute(self, context):
        keyframe_index = {"diffuse_color": 0, "specular_color": 3,
                          "emit": 6, "ambient": 7, "translucency": 8}
        objs = []
        for obj in bpy.context.scene.objects:
            matched = re.search(context.scene.save_keyframes_id_key, obj.name)
            if matched:
                objs.append(obj)

        keyframes = {}
        start_frame = context.scene.save_keyframes_start_frame
        end_frame = context.scene.save_keyframes_end_frame
        for obj in objs:

            # extract keyframes
            # [[keyframe_index, frame, value], [], ...]
            kfs = []
            for fc in obj.active_material.animation_data.action.fcurves:
                if fc.data_path.endswith(("diffuse_color", "specular_color",
                                          "emit", "ambient", "translucency")):
                    kfs += [[keyframe_index[fc.data_path] + fc.array_index, i.co[0], i.co[1]]
                            for i in fc.keyframe_points
                            if i.co[0] >= start_frame and i.co[0] <= end_frame]

            # register keyframes
            # {obj_name: {
            #     frame_1: [
            #               diffuse_color_r,diffuse_color_g,diffuse_color_b,
            #               specular_color_r,specular_color_g,specular_color_b,
            #               emit,ambient,translucency
            #              ],
            #     frame_2: [], ...}
            keyframes[obj.name] = {}
            for key in kfs:
                fr = str(int(key[1]))
                if fr in keyframes[obj.name]:
                    keyframes[obj.name][fr][key[0]] = key[2]
                else:
                    keyframes[obj.name][fr] = [
                        0, 0, 0, 0, 0, 0, 1, 1, 1]
                    keyframes[obj.name][fr][key[0]] = key[2]

        if bpy.data.is_saved:
            filepath = bpy.path.abspath(
                "//" + context.scene.save_keyframes_file_name + ".csv")
            with open(filepath, "w") as f:
                for uav, frames in keyframes.items():
                    for frame, v in frames.items():
                        v = map(str, v)
                        f.write(uav + "," + frame + "," + ",".join(v) + "\n")
        else:
            raise Exception("Please save blender file first.")
        return {"FINISHED"}

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene, "save_keyframes_id_key")
        col.prop(context.scene, "save_keyframes_start_frame")
        col.prop(context.scene, "save_keyframes_end_frame")
        col.prop(context.scene, "save_keyframes_file_name")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SaveSelectionPositions(bpy.types.Operator):

    bl_idname = "object.save_selection_positions"
    bl_label = "save selection positions"
    bl_description = "Save selected objects\' current positions."
    bl_options = {"REGISTER", "UNDO"}
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    # main
    def execute(self, context):
        with open(self.filepath, "w") as f:
            for obj in [o for o in bpy.context.scene.objects if o.select]:
                f.write(
                    obj.name + "," + str(bpy.context.scene.frame_current) + ","
                    + str(obj.location[0]) + "," + str(obj.location[1])
                    + "," + str(obj.location[2]) + ","
                    + str(obj.rotation_euler[0]) +
                    "," + str(obj.rotation_euler[1])
                    + "," + str(obj.rotation_euler[2]) + ","
                    + str(obj.scale[0]) + "," + str(obj.scale[1]) + "," + str(obj.scale[2]) + "\n")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = ".csv"
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SaveVerticesPositionsOfMesh(bpy.types.Operator):

    bl_idname = "object.save_vertices_positions_of_mesh"
    bl_label = "save vertices positions of mesh"
    bl_description = "Save vertices\' positions of active mesh."
    bl_options = {"REGISTER", "UNDO"}
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    # main
    def execute(self, context):
        obj = bpy.context.active_object
        if obj.type == "MESH":
            verts = [obj.matrix_world * vert.co for vert in obj.data.vertices]
        elif obj.type == "CURVE":
            verts = [p.co[:3] for p in obj.data.splines[0].points]
        else:
            raise Exception("Unsupported type: {}.".format(obj.type))
        with open(self.filepath, "w") as f:
            for v in verts:
                f.write(str(v[0]) + "," + str(v[1]) + "," + str(v[2]) + "\n")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = ".csv"
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator(SaveKeyframes.bl_idname, text="Save object keyframes")
    self.layout.operator(SaveMaterialKeyframes.bl_idname,
                         text="Save material keyframes")
    self.layout.operator(SaveSelectionPositions.bl_idname,
                         text="Save selection positions")
    self.layout.operator(SaveVerticesPositionsOfMesh.bl_idname,
                         text="Save vertices positions of mesh")


def register_shortcut():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # register shortcut in 3d view
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        # key
        kmi = km.keymap_items.new(
            idname=SaveKeyframes.bl_idname,
            type="K",
            value="PRESS",
            shift=False,
            ctrl=True,
            alt=True)
        # register to shortcut key list
        addon_keymaps.append((km, kmi))


def unregister_shortcut():
    for km, kmi in addon_keymaps:
        # unregister shortcut key
        km.keymap_items.remove(kmi)
    # clear shortcut key list
    addon_keymaps.clear()


def register():
    unregister_shortcut()
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_object_animation.append(menu_func)
    bpy.types.Scene.save_keyframes_id_key\
        = bpy.props.StringProperty(
            name="id key (regular expression)",
            description="select object only which matches to this expression.",
            default="")
    bpy.types.Scene.save_keyframes_start_frame\
        = bpy.props.IntProperty(
            name="start frame",
            description="parent id in group")
    bpy.types.Scene.save_keyframes_end_frame\
        = bpy.props.IntProperty(
            name="end frame",
            description="parent id in group")
    bpy.types.Scene.save_keyframes_file_name\
        = bpy.props.StringProperty(
            name="export file name",
            description="Csv file name to save.",
            default="keyframes")
    register_shortcut()


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_object_animation.remove(menu_func)
    del bpy.types.Scene.save_keyframes_id_key
    del bpy.types.Scene.save_keyframes_start_frame
    del bpy.types.Scene.save_keyframes_end_frame
    del bpy.types.Scene.save_keyframes_file_name


if __name__ == "__main__":
    register()
