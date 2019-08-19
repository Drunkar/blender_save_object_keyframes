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
from mathutils import Vector

bl_info = {
    "name": "save object keyframes",
    "author": "Drunkar",
    "version": (0, 9, 4),
    "blender": (2, 80, 0),
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
            if obj.animation_data is not None:
                fcurves = obj.animation_data.action.fcurves
            elif obj.parent.animation_data is not None:
                fcurves = obj.parent.animation_data.action.fcurves
            elif obj.parent.parent.animation_data is not None:
                fcurves = obj.parent.parent.animation_data.action.fcurves
            elif obj.parent.parent.parent.animation_data is not None:
                fcurves = obj.parent.parent.parent.animation_data.action.fcurve
            elif obj.parent.parent.parent.parent.animation_data is not None:
                fcurves = obj.parent.parent.parent.parent.animation_data.action.fcurve
            elif obj.parent.parent.parent.parent.parent.animation_data is not None:
                fcurves = obj.parent.parent.parent.parent.parent.animation_data.action.fcurve
            elif obj.parent.parent.parent.parent.parent.parent.animation_data is not None:
                fcurves = obj.parent.parent.parent.parent.parent.parent.animation_data.action.fcurve
            elif obj.parent.parent.parent.parent.parent.parent.parent.animation_data is not None:
                fcurves = obj.parent.parent.parent.parent.parent.parent.parent.animation_data.action.fcurve
            else:
                fcurves = []
            frames = []
            for fc in fcurves:
                if fc.data_path.endswith(("location", "rotation_euler", "scale")):
                    frames += [int(i.co[0]) for i in fc.keyframe_points if i.co[0] >= start_frame and i.co[0] <= end_frame]
            frames = list(set(frames))

            # register keyframes
            # {obj_name: {
            #     frame_1: [
            #               location_0,location_1,location_2,
            #               rotation_euler_0,rotation_euler_1,rotation_euler_2,
            #               sale_0,scale_1,scale_2
            #              ],
            #     frame_2: [], ...}
            keyframes[obj.name] = {}
            for frame in frames:
                bpy.context.scene.frame_set(frame)
                loc = obj.matrix_world.to_translation()
                rot = obj.matrix_world.to_euler()
                sca = obj.matrix_world.to_scale()
                keyframes[obj.name][str(frame)] = [loc[0], loc[1], loc[2], rot[0], rot[1], rot[2], sca[0], sca[1], sca[2]]

        if bpy.data.is_saved:
            filepath = bpy.path.abspath(
                "//" + context.scene.save_keyframes_file_name + ".csv")
            with open(filepath, "w", encoding="utf-8") as f:
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


class SaveAnimations(bpy.types.Operator):

    bl_idname = "object.save_animations"
    bl_label = "save positions of each frames to csv"
    bl_description = "Save positions of object, which matched a keyword."
    bl_options = {"REGISTER", "UNDO"}

    # main
    def execute(self, context):
        objs = []
        for name, obj in bpy.context.scene.objects.items():
            if obj.select_get():
                matched = re.search(context.scene.save_keyframes_id_key, name)
                if matched:
                    objs.append(obj)

        start_frame = context.scene.save_keyframes_start_frame
        end_frame = context.scene.save_keyframes_end_frame
        interval = context.scene.save_keyframes_interval
        last_frame_is_included = (end_frame - start_frame) % interval == 0
        keyframes = {}
        for obj in objs:
            # register keyframes
            # {obj_name: {
            #     frame_1: [
            #               location_0,location_1,location_2,
            #               rotation_euler_0,rotation_euler_1,rotation_euler_2,
            #               sale_0,scale_1,scale_2
            #              ],
            #     frame_2: [], ...}
            keyframes[obj.name] = {}
            for frame in range(start_frame, end_frame+1)[::interval]:
                bpy.context.scene.frame_set(frame)
                loc = obj.matrix_world.to_translation()
                rot = obj.matrix_world.to_euler()
                sca = obj.matrix_world.to_scale()
                keyframes[obj.name][str(frame)] = [loc[0], loc[1], loc[2], rot[0], rot[1], rot[2], sca[0], sca[1], sca[2]]
            if not last_frame_is_included:
                bpy.context.scene.frame_set(end_frame)
                loc = obj.matrix_world.to_translation()
                rot = obj.matrix_world.to_euler()
                sca = obj.matrix_world.to_scale()
                keyframes[obj.name][str(end_frame)] = [loc[0], loc[1], loc[2], rot[0], rot[1], rot[2], sca[0], sca[1], sca[2]]

        if bpy.data.is_saved:
            filepath = bpy.path.abspath(
                "//" + context.scene.save_keyframes_file_name + ".csv")
            with open(filepath, "w", encoding="utf-8") as f:
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
        col.prop(context.scene, "save_keyframes_interval")
        col.prop(context.scene, "save_keyframes_file_name")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SaveAnimationsOfMesh(bpy.types.Operator):

    bl_idname = "object.save_animations_of_mesh"
    bl_label = "save positions of each frames in mesh to csv"
    bl_description = "Save positions of object, which matched a keyword."
    bl_options = {"REGISTER", "UNDO"}

    # main
    def execute(self, context):
        objs = []
        for name, obj in bpy.context.scene.objects.items():
            matched = re.search(context.scene.save_keyframes_id_key, name)
            if matched:
                objs.append(obj)

        start_frame = context.scene.save_keyframes_start_frame
        end_frame = context.scene.save_keyframes_end_frame
        interval = context.scene.save_keyframes_interval
        last_frame_is_included = (end_frame - start_frame) % interval == 0
        filepath = bpy.path.abspath(
            "//" + context.scene.save_keyframes_file_name + ".csv")
        with open(filepath, "w", encoding="utf-8") as f:
            for obj in objs:
                # register keyframes
                # {obj_name: {
                #     frame_1: [
                #               location_0,location_1,location_2,
                #               rotation_euler_0,rotation_euler_1,rotation_euler_2,
                #               sale_0,scale_1,scale_2
                #              ],
                #     frame_2: [], ...}
                hide_initial = obj.hide_viewport
                obj.hide_viewport = False
                for frame in range(start_frame, end_frame+1)[::interval]:
                    bpy.context.scene.frame_set(frame)
                    depsgraph = bpy.context.evaluated_depsgraph_get()
                    ob_eval = obj.evaluated_get(depsgraph)
                    mesh = ob_eval.to_mesh()
                    mesh.transform(ob_eval.matrix_world) # apply modifiers with preview settings
                    verts = [vert.co for vert in mesh.vertices]
                    for i, v in enumerate(verts[::-1]):
                        f.write(obj.name + "_" + ("000000" + str(i+1))[-6:] + "," + str(frame) + "," + str(v[0]) + "," + str(v[1]) + "," + str(v[2]) + ",0,0,0,1.0,1.0,1.0\n")

                if not last_frame_is_included:
                    bpy.context.scene.frame_set(end_frame)
                    depsgraph = bpy.context.evaluated_depsgraph_get()
                    ob_eval = obj.evaluated_get(depsgraph)
                    mesh = ob_eval.to_mesh()
                    mesh.transform(ob_eval.matrix_world) # apply modifiers with preview settings
                    verts = [vert.co for vert in mesh.vertices]
                    for i, v in enumerate(verts[::-1]):
                        f.write(obj.name + "_" + ("000000" + str(i+1))[-6:] + "," + str(frame) + "," + str(v[0]) + "," + str(v[1]) + "," + str(v[2]) + ",0,0,0,1.0,1.0,1.0\n")
                obj.hide_viewport = hide_initial
        return {"FINISHED"}

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene, "save_keyframes_id_key")
        col.prop(context.scene, "save_keyframes_start_frame")
        col.prop(context.scene, "save_keyframes_end_frame")
        col.prop(context.scene, "save_keyframes_interval")
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
            with open(filepath, "w", encoding="utf-8") as f:
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
        with open(self.filepath, "w", encoding="utf-8") as f:
            for obj in [o for o in bpy.context.scene.objects if o.select_get()][::-1]:
                loc = obj.matrix_world.to_translation()
                rot = obj.matrix_world.to_euler()
                sca = obj.matrix_world.to_scale()
                f.write(
                    obj.name + "," + str(bpy.context.scene.frame_current) + ","
                    + str(loc[0]) + "," + str(loc[1])
                    + "," + str(loc[2]) + ","
                    + str(rot[0]) +
                    "," + str(rot[1])
                    + "," + str(rot[2]) + ","
                    + str(sca[0]) + "," + str(sca[1]) + "," + str(sca[2]) + "\n")
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
            hide_initial = obj.hide_viewport
            obj.hide_viewport = False
            depsgraph = bpy.context.evaluated_depsgraph_get()
            ob_eval = obj.evaluated_get(depsgraph)
            mesh = ob_eval.to_mesh()
            mesh.transform(ob_eval.matrix_world) # apply modifiers with preview settings
            verts = [vert.co for vert in mesh.vertices]
            obj.hide_viewport = hide_initial
        elif obj.type == "CURVE":
            verts = [(obj.matrix_world @ Vector(p.co[:3])) for p in obj.data.splines[0].points]
        else:
            raise Exception("Unsupported type: {}.".format(obj.type))
        with open(self.filepath, "w", encoding="utf-8") as f:
            for v in verts[::-1]:
                f.write(str(v[0]) + "," + str(v[1]) + "," + str(v[2]) + "\n")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = ".csv"
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SaveMeshAnimationVertices(bpy.types.Operator):

    bl_idname = "object.save_mesh_animation_vertices"
    bl_label = "save vertices positions of mesh animation"
    bl_description = "Save vertices\' positions of active mesh."
    bl_options = {"REGISTER", "UNDO"}
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    # main
    def execute(self, context):
        obj = bpy.context.active_object
        if obj.type != "MESH":
            raise Exception("Unsupported type: {}.".format(obj.type))

        hide_initial = obj.hide_viewport
        obj.hide_viewport = False
        with open(self.filepath, "w", encoding="utf-8") as f:
            for frame in range(bpy.context.scene.frame_current, 251):
                bpy.context.scene.frame_set(frame)
                depsgraph = bpy.context.evaluated_depsgraph_get()
                ob_eval = obj.evaluated_get(depsgraph)
                mesh = ob_eval.to_mesh()
                mesh.transform(ob_eval.matrix_world) # apply modifiers with preview settings
                verts = [vert.co for vert in mesh.vertices]
                for i, v in enumerate(verts[::-1]):
                    f.write("OBJ_" + ("000000" + str(i+1))[-6:] + "," + str(frame) + "," + str(v[0]) + "," + str(v[1]) + "," + str(v[2]) + ",0,0,0,1.0,1.0,1.0\n")
        obj.hide_viewport = hide_initial
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = ".csv"
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SaveUVMapOfMesh(bpy.types.Operator):

    bl_idname = "object.save_uv_map_of_mesh"
    bl_label = "save uv vertices positions of mesh"
    bl_description = "Save uv vertices\' positions of active mesh."
    bl_options = {"REGISTER", "UNDO"}
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    # main
    def execute(self, context):
        obj = bpy.context.active_object
        if obj.type == "MESH":
            hide_initial = obj.hide_viewport
            obj.hide_viewport = False
            depsgraph = bpy.context.evaluated_depsgraph_get()
            ob_eval = obj.evaluated_get(depsgraph)
            mesh = ob_eval.to_mesh()
            mesh.transform(ob_eval.matrix_world)  # apply modifiers with preview settings
            uv_layer = obj.data.uv_layers.active.data
            uv_pos = {}
            for lo in mesh.loops:
                p = [str(v) for v in mesh.vertices[lo.vertex_index].co]
                p = ",".join(p)
                if p not in uv_pos:
                    uv_pos[p] = uv_layer[lo.index].uv
                else:
                    if uv_pos[p][1] == uv_layer[lo.index].uv[1]:
                        if uv_pos[p][0] > uv_layer[lo.index].uv[0]:
                            uv_pos[p] = uv_layer[lo.index].uv
                    elif uv_pos[p][1] < uv_layer[lo.index].uv[1]:
                            uv_pos[p] = uv_layer[lo.index].uv

            verts = [",".join([str(vert.co[0]), str(vert.co[1]), str(vert.co[2])]) for vert in mesh.vertices]
            obj.hide_viewport = hide_initial
        else:
            raise Exception("Unsupported type: {}.".format(obj.type))

        with open(self.filepath, "w", encoding="utf-8") as f:
            for v in verts[::-1]:
                f.write(str(uv_pos[v][0]) + "," + str(uv_pos[v][1]) + "\n")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = ".csv"
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator(SaveKeyframes.bl_idname, text="Save object keyframes")
    self.layout.operator(SaveAnimations.bl_idname, text="Save positions of each frame")
    self.layout.operator(SaveAnimationsOfMesh.bl_idname, text="Save positions of mesh of each frame")
    self.layout.operator(SaveMaterialKeyframes.bl_idname,
                         text="Save material keyframes")
    self.layout.operator(SaveSelectionPositions.bl_idname,
                         text="Save selection positions")
    self.layout.operator(SaveVerticesPositionsOfMesh.bl_idname,
                         text="Save vertices positions of mesh")
    self.layout.operator(SaveMeshAnimationVertices.bl_idname,
                         text="Save vertices positions of mesh animation")
    self.layout.operator(SaveUVMapOfMesh.bl_idname,
                         text="Save uv vertices positions of mesh")


def register_shortcut():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            idname=SaveKeyframes.bl_idname,
            type="K",
            value="PRESS",
            shift=False,
            ctrl=True,
            alt=True)
        addon_keymaps.append((km, kmi))


def unregister_shortcut():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


classes = (
    SaveKeyframes,
    SaveAnimations,
    SaveAnimationsOfMesh,
    SaveMaterialKeyframes,
    SaveSelectionPositions,
    SaveVerticesPositionsOfMesh,
    SaveMeshAnimationVertices,
    SaveUVMapOfMesh,
)


def register():
    unregister_shortcut()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_animation.append(menu_func)
    bpy.types.Scene.save_keyframes_id_key\
        = bpy.props.StringProperty(
            name="id key (regular expression)",
            description="select object only which matches to this expression.",
            default="")
    bpy.types.Scene.save_keyframes_start_frame\
        = bpy.props.IntProperty(
            name="start frame",
            description="start frame")
    bpy.types.Scene.save_keyframes_end_frame\
        = bpy.props.IntProperty(
            name="end frame",
            description="end frame")
    bpy.types.Scene.save_keyframes_interval\
        = bpy.props.IntProperty(
            name="interval",
            description="save frame interval")
    bpy.types.Scene.save_keyframes_file_name\
        = bpy.props.StringProperty(
            name="export file name",
            description="Csv file name to save.",
            default="keyframes")
    register_shortcut()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object_animation.remove(menu_func)
    del bpy.types.Scene.save_keyframes_id_key
    del bpy.types.Scene.save_keyframes_start_frame
    del bpy.types.Scene.save_keyframes_end_frame
    del bpy.types.Scene.save_keyframes_file_name


if __name__ == "__main__":
    register()
