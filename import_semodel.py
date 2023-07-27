import bpy
import bmesh
import os
import array
from mathutils import *
from math import *
from bpy_extras.image_utils import load_image
from . import semodel as SEModel


def __build_image_path__(asset_path, image_path):
    root_path = os.path.dirname(asset_path)
    return os.path.join(root_path, image_path)

def image_has_alpha(img):
    return img.pixels[3] != 1.0

def load(self, context, filepath="", isMap=False):
    ob = bpy.context.object
    scene = bpy.context.scene
    model_name = os.path.splitext(os.path.basename(filepath))[0]

    model = SEModel.Model(filepath)

    mesh_objs = []
    mesh_mats = []

    mats = []
    sub_mats = []

    for mat in model.materials:
        if isMap:
            mat_name = mat.name[-1]

            if mat_name == "0":
                mats.append(mat)
            elif mat_name == "1":
                mats.append(mat)
            elif mat_name == "2":
                sub_mats.append(mat)
        else:
            mats.append(mat)
            
    for mat in mats:
        new_mat = bpy.data.materials.get(mat.name)
        if new_mat is not None:
            mesh_mats.append(new_mat)
            continue

        new_mat = bpy.data.materials.new(name=mat.name)
        new_mat.use_nodes = True
        new_mat.blend_method = "CLIP"
        new_mat.shadow_method = "CLIP"

        # Create / Get Nodes
        bsdf_shader = new_mat.node_tree.nodes["Principled BSDF"]
        normal_map = new_mat.node_tree.nodes.new("ShaderNodeNormalMap")
        invert_node = new_mat.node_tree.nodes.new("ShaderNodeInvert")
        seperate_color_node = new_mat.node_tree.nodes.new("ShaderNodeSeparateColor")
        combine_color_node = new_mat.node_tree.nodes.new("ShaderNodeCombineColor")
        combine_color_node.inputs["Blue"].default_value = 1.0
        material_color_map = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
        material_specular_map = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
        material_normal_map = new_mat.node_tree.nodes.new("ShaderNodeTexImage")

        if ("glass" in mat.name or mat.name.startswith("decal_")): #or mat.name.endswith("_blend")) and len(matList) == 1 and "fiberglass" not in mat.name:
            new_mat.blend_method = "BLEND"
            bsdf_shader.inputs["Transmission"].default_value = 1.0

        hasDiffuseAlpha = True
        hasSpec1 = True
        hasSpec2 = True
        hasNormal1 = True
        hasNormal2 = True

        # Load Textures
        try:
            material_color_map.image = bpy.data.images.load(
                __build_image_path__(filepath, mat.inputData.diffuseMap))
            
            hasDiffuseAlpha = image_has_alpha(material_color_map.image)
        except RuntimeError:
            pass
        
        try:
            material_specular_map.image = bpy.data.images.load(
                __build_image_path__(filepath, mat.inputData.specularMap))
            material_specular_map.image.colorspace_settings.name = "Non-Color"
        except RuntimeError:
            new_mat.node_tree.nodes.remove(material_specular_map)
            hasSpec1 = False
            pass

        try:
            material_normal_map.image = bpy.data.images.load(
                __build_image_path__(filepath, mat.inputData.normalMap))
            material_normal_map.image.colorspace_settings.name = "Non-Color"
        except RuntimeError:
            new_mat.node_tree.nodes.remove(material_normal_map)
            hasNormal1 = False
            pass
                
        if mat.name[-1] == "1" and isMap:
            secondary_invert_node = new_mat.node_tree.nodes.new("ShaderNodeInvert")
            secondary_seperate_color_node = new_mat.node_tree.nodes.new("ShaderNodeSeparateColor")
            secondary_combine_color_node = new_mat.node_tree.nodes.new("ShaderNodeCombineColor")
            secondary_combine_color_node.inputs["Blue"].default_value = 1.0
            secondary_material_color_map = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
            secondary_material_specular_map = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
            secondary_material_normal_map = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
            mix_seperate_color_node = new_mat.node_tree.nodes.new("ShaderNodeSeparateColor")
            mix_color_attribute_node = new_mat.node_tree.nodes.new("ShaderNodeVertexColor")

            blend_texture_node = new_mat.node_tree.nodes.new("ShaderNodeGroup")
            blend_texture_node.node_tree = bpy.data.node_groups['BlendTextures']

            secondary_mat_name = mat.name[mat.name.find(":") + 1:-1] + "2"
            secondary_mat = mat;
            for secondary_mat_i in sub_mats:
                if secondary_mat_i.name == secondary_mat_name:
                    secondary_mat = secondary_mat_i;
                    break

                # Load Textures
            try:
                secondary_material_color_map.image = bpy.data.images.load(
                    __build_image_path__(filepath, secondary_mat.inputData.diffuseMap))
            except RuntimeError:
                pass
            
            try:
                secondary_material_specular_map.image = bpy.data.images.load(
                    __build_image_path__(filepath, secondary_mat.inputData.specularMap))
                secondary_material_specular_map.image.colorspace_settings.name = "Non-Color"
            except RuntimeError:
                new_mat.node_tree.nodes.remove(secondary_material_specular_map)
                new_mat.node_tree.nodes.remove(secondary_invert_node)
                hasSpec2 = False
                pass

            try:
                secondary_material_normal_map.image = bpy.data.images.load(
                    __build_image_path__(filepath, secondary_mat.inputData.normalMap))
                secondary_material_normal_map.image.colorspace_settings.name = "Non-Color"
            except RuntimeError:
                hasNormal2 = False
                new_mat.node_tree.nodes.remove(secondary_material_normal_map)
                pass

            blend_texture_node.location = (-400, 200)
            material_color_map.location = (-1150, 1000)
            secondary_material_color_map.location = (-1150, 600)
            mix_seperate_color_node.location = (-520, -555)
            mix_color_attribute_node.location = (-520, -820)
            mix_color_attribute_node.layer_name = "Color"

            if hasSpec1:
                material_specular_map.location = (-1150, -400)
                invert_node.location = (-850, -550)
            else:
                if hasDiffuseAlpha:
                    invert_node.location = (-850, -550)
                else:
                    new_mat.node_tree.nodes.remove(invert_node)
            if hasSpec2:
                secondary_invert_node.location = (-800, -800)
                secondary_material_specular_map.location = (-1150, -800)
            if hasNormal1:
                material_normal_map.location = (-1500, 200)
                seperate_color_node.location = (-1220, 200)
                combine_color_node.location = (-1050, 200)
            else:
                new_mat.node_tree.nodes.remove(seperate_color_node)
                new_mat.node_tree.nodes.remove(combine_color_node)
            if hasNormal2:
                secondary_material_normal_map.location = (-1500, -200)
                secondary_seperate_color_node.location = (-1220, -80)
                secondary_combine_color_node.location = (-1050, -80)
            else:
                new_mat.node_tree.nodes.remove(secondary_seperate_color_node)
                new_mat.node_tree.nodes.remove(secondary_combine_color_node)
            if hasNormal1 or hasNormal2:
                normal_map.location = (-180, -280)
            else:
                new_mat.node_tree.nodes.remove(normal_map)

            new_mat.node_tree.links.new(
                mix_seperate_color_node.inputs["Color"], mix_color_attribute_node.outputs["Color"])

            new_mat.node_tree.links.new(
                blend_texture_node.inputs["Vertex Alpha"], mix_seperate_color_node.outputs["Green"])

            new_mat.node_tree.links.new(
                blend_texture_node.inputs["Base Color_1"], material_color_map.outputs["Color"])

            new_mat.node_tree.links.new(
                blend_texture_node.inputs["Base Color_2"], secondary_material_color_map.outputs["Color"])

            new_mat.node_tree.links.new(
                blend_texture_node.inputs["Alpha"], secondary_material_color_map.outputs["Alpha"])

            new_mat.node_tree.links.new(
                bsdf_shader.inputs["Base Color"], blend_texture_node.outputs["Base Color"])

            new_mat.node_tree.links.new(
                bsdf_shader.inputs["Specular"], blend_texture_node.outputs["Specular"])

            new_mat.node_tree.links.new(
                bsdf_shader.inputs["Roughness"], blend_texture_node.outputs["Roughness"])
            if hasSpec1:
                new_mat.node_tree.links.new(
                    invert_node.inputs["Color"], material_specular_map.outputs["Alpha"])
                
                new_mat.node_tree.links.new(
                    blend_texture_node.inputs["Specular_1"], material_specular_map.outputs["Color"])
                
                new_mat.node_tree.links.new(
                    blend_texture_node.inputs["Roughness_1"], invert_node.outputs["Color"])
            else:
                if hasDiffuseAlpha:
                    new_mat.node_tree.links.new(
                        invert_node.inputs["Color"], material_color_map.outputs["Alpha"])
                    
                    new_mat.node_tree.links.new(
                        blend_texture_node.inputs["Roughness_1"], invert_node.outputs["Color"])

            if hasSpec2:
                new_mat.node_tree.links.new(
                    secondary_invert_node.inputs["Color"], secondary_material_specular_map.outputs["Alpha"])
                
                new_mat.node_tree.links.new(
                    blend_texture_node.inputs["Roughness_2"], secondary_invert_node.outputs["Color"])
                
                new_mat.node_tree.links.new(
                    blend_texture_node.inputs["Specular_2"], secondary_material_specular_map.outputs["Color"])
            
            if hasNormal1:
                new_mat.node_tree.links.new(
                    seperate_color_node.inputs["Color"], material_normal_map.outputs["Color"])
                
                new_mat.node_tree.links.new(
                    combine_color_node.inputs["Red"], seperate_color_node.outputs["Red"])
        
                new_mat.node_tree.links.new(
                    combine_color_node.inputs["Green"], seperate_color_node.outputs["Green"])
                
                new_mat.node_tree.links.new(
                    blend_texture_node.inputs["Normal_1"], combine_color_node.outputs["Color"])

            if hasNormal2:
                new_mat.node_tree.links.new(
                    secondary_seperate_color_node.inputs["Color"], secondary_material_normal_map.outputs["Color"])
                
                new_mat.node_tree.links.new(
                    secondary_combine_color_node.inputs["Red"], secondary_seperate_color_node.outputs["Red"])
        
                new_mat.node_tree.links.new(
                    secondary_combine_color_node.inputs["Green"], secondary_seperate_color_node.outputs["Green"])
                
                new_mat.node_tree.links.new(
                    blend_texture_node.inputs["Normal_2"], secondary_combine_color_node.outputs["Color"])

            if hasNormal1 or hasNormal2:
                new_mat.node_tree.links.new(
                    normal_map.inputs["Color"], blend_texture_node.outputs["Normal"])

                new_mat.node_tree.links.new(
                    bsdf_shader.inputs["Normal"], normal_map.outputs["Normal"])
        else:
            # Node Location
            material_color_map.location = (-600, 350)

            if hasSpec1:
                material_specular_map.location = (-600, 0)
                invert_node.location = (-250, 0)
            else:
                if hasDiffuseAlpha:
                    invert_node.location = (-250, 0)
                else:
                    new_mat.node_tree.nodes.remove(invert_node)
            if hasNormal1:
                material_normal_map.location = (-900, -350)
                normal_map.location = (-250, -300)
                seperate_color_node.location = (-610, -450)
                combine_color_node.location = (-450, -450)
            else:
                new_mat.node_tree.nodes.remove(normal_map)
                new_mat.node_tree.nodes.remove(seperate_color_node)
                new_mat.node_tree.nodes.remove(combine_color_node)  

            # Connect Nodes
            new_mat.node_tree.links.new(
                bsdf_shader.inputs["Base Color"], material_color_map.outputs["Color"])
            
            if hasSpec1:
                new_mat.node_tree.links.new(
                    bsdf_shader.inputs["Alpha"], material_color_map.outputs["Alpha"])

                new_mat.node_tree.links.new(
                    bsdf_shader.inputs["Specular"], material_specular_map.outputs["Color"])
                
                new_mat.node_tree.links.new(
                    invert_node.inputs["Color"], material_specular_map.outputs["Alpha"])
            else:
                if hasDiffuseAlpha:
                    new_mat.node_tree.links.new(
                        invert_node.inputs["Color"], material_color_map.outputs["Alpha"])
                    
                    new_mat.node_tree.links.new(
                        bsdf_shader.inputs["Roughness"], invert_node.outputs["Color"])
                
            if hasNormal1:
                new_mat.node_tree.links.new(
                    seperate_color_node.inputs["Color"], material_normal_map.outputs["Color"])

                new_mat.node_tree.links.new(
                    normal_map.inputs["Color"], combine_color_node.outputs["Color"])

                new_mat.node_tree.links.new(
                    bsdf_shader.inputs["Normal"], normal_map.outputs["Normal"])
                
                new_mat.node_tree.links.new(
                    combine_color_node.inputs["Green"], seperate_color_node.outputs["Green"])

                new_mat.node_tree.links.new(
                    combine_color_node.inputs["Red"], seperate_color_node.outputs["Red"])
                
        mesh_mats.append(new_mat)

    i = 0
    for mesh in model.meshes:
        new_mesh = bpy.data.meshes.new("SEModelMesh")
        blend_mesh = bmesh.new()

        vertex_color_layer = blend_mesh.loops.layers.color.new("Color")
        vertex_weight_layer = blend_mesh.verts.layers.deform.new()

        vertex_uv_layers = []
        for uvLayer in range(mesh.matReferenceCount):
            vertex_uv_layers.append(
                blend_mesh.loops.layers.uv.new("UVSet_%d" % uvLayer))

        for vert_idx, vert in enumerate(mesh.vertices):
            blend_mesh.verts.new(Vector(vert.position))

        blend_mesh.verts.ensure_lookup_table()

        # Loop and assign weights, if any
        for vert_idx, vert in enumerate(mesh.vertices):
            for weight in vert.weights:
                # Weights are valid when value is > 0.0
                if (weight[1] > 0.0):
                    blend_mesh.verts[vert_idx][vertex_weight_layer][weight[0]] = weight[1]

        vertex_normal_buffer = []
        face_index_map = [0, 2, 1]

        def setup_face_vert(bm_face):
            for loop_idx, loop in enumerate(bm_face.loops):
                vert_idx = face.indices[face_index_map[loop_idx]]

                # Build buffer of normals
                vertex_normal_buffer.append(mesh.vertices[vert_idx].normal)

                # Assign vertex uv layers
                for uvLayer in range(mesh.matReferenceCount):
                    # Blender also has pathetic uv layout
                    uv = Vector(mesh.vertices[vert_idx].uvLayers[uvLayer])
                    uv.y = 1.0 - uv.y

                    # Set the UV to the layer
                    loop[vertex_uv_layers[uvLayer]].uv = uv

                # Assign vertex colors
                loop[vertex_color_layer] = mesh.vertices[vert_idx].color

        for face in mesh.faces:
            indices = [blend_mesh.verts[face.indices[0]],
                       blend_mesh.verts[face.indices[2]], blend_mesh.verts[face.indices[1]]]

            try:
                new_face = blend_mesh.faces.new(indices)
            except ValueError:
                continue
            else:
                setup_face_vert(new_face)

        blend_mesh.to_mesh(new_mesh)

        # Begin vertex normal assignment logic
        new_mesh.create_normals_split()

        for loop_idx, loop in enumerate(new_mesh.loops):
            new_mesh.loops[loop_idx].normal = vertex_normal_buffer[loop_idx]

        new_mesh.validate(clean_customdata=False)

        clnors = array.array('f', [0.0] * (len(new_mesh.loops) * 3))
        new_mesh.loops.foreach_get("normal", clnors)

        # Enable smoothing - must be BEFORE normals_split_custom_set, etc.
        polygon_count = len(new_mesh.polygons)
        new_mesh.polygons.foreach_set("use_smooth", [True] * polygon_count)

        new_mesh.normals_split_custom_set(tuple(zip(*(iter(clnors),) * 3)))
        new_mesh.use_auto_smooth = True

        # Add the mesh to the scene
        obj = bpy.data.objects.new("%s_%s" % (
            model_name, new_mesh.name), new_mesh)
        mesh_objs.append(obj)

        # Apply mesh materials
        for mat_index in mesh.materialReferences:
            if mat_index < 0:
                continue
            if mat_index == 112:
                i = 1

            obj.data.materials.append(mesh_mats[mat_index])

        bpy.context.view_layer.active_layer_collection.collection.objects.link(
            obj)
        bpy.context.view_layer.objects.active = obj

        # Create vertex groups for weights
        for bone in model.bones:
            obj.vertex_groups.new(name=bone.name)

        #if i == 1:
            #break

    # Create the skeleton
    armature = bpy.data.armatures.new("%s_amt" % model_name)
    armature.display_type = "STICK"

    skel_obj = bpy.data.objects.new("%s_skel" % model_name, armature)
    skel_obj.show_in_front = True

    bpy.context.view_layer.active_layer_collection.collection.objects.link(
        skel_obj)
    bpy.context.view_layer.objects.active = skel_obj

    # Begin edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    bone_mats = {}
    for bone in model.bones:
        new_bone = armature.edit_bones.new(bone.name)
        new_bone.tail = 0, 0.05, 0  # Blender is so bad it removes bones if they have 0 length

        # Calculate local-space position matrix
        mat_rot = Quaternion((bone.localRotation[3], bone.localRotation[0],
                              bone.localRotation[1], bone.localRotation[2])).to_matrix().to_4x4()
        mat_trans = Matrix.Translation(Vector(bone.localPosition))

        final_mat = mat_trans @ mat_rot

        bone_mats[bone.name] = final_mat

        # Set parent if we have any
        if bone.boneParent > -1:
            new_bone.parent = armature.edit_bones[bone.boneParent]

    bpy.context.view_layer.objects.active = skel_obj
    bpy.ops.object.mode_set(mode='POSE')

    for bone in skel_obj.pose.bones:
        bone.matrix_basis.identity()
        bone.matrix = bone_mats[bone.name]

    bpy.ops.pose.armature_apply()

    # Create natural bone-line structure
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=2)
    bone_vis = bpy.context.active_object
    bone_vis.data.name = bone_vis.name = "semodel_bone_vis"
    bone_vis.use_fake_user = True
    bpy.context.view_layer.active_layer_collection.collection.objects.unlink(
        bone_vis)
    bpy.context.view_layer.objects.active = skel_obj

    # Calculate armature dimensions...
    maxs = [0, 0, 0]
    mins = [0, 0, 0]

    j = 0
    for bone in armature.bones:
        for i in range(3):
            maxs[i] = max(maxs[i], bone.head_local[i])
            mins[i] = min(mins[i], bone.head_local[i])

    dimensions = []
    for i in range(3):
        dimensions.append(maxs[i] - mins[i])

    # very small indeed, but a custom bone is used for display
    length = max(0.001, (dimensions[0] + dimensions[1] + dimensions[2]) / 600)

    # Apply spheres
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in [armature.edit_bones[b.name] for b in model.bones]:
        bone.tail = bone.head + (bone.tail - bone.head).normalized() * length
        skel_obj.pose.bones[bone.name].custom_shape = bone_vis

    # Reset the view mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Set armature deform for weights
    for mesh_obj in mesh_objs:
        mesh_obj.parent = skel_obj
        modifier = mesh_obj.modifiers.new('Armature Rig', 'ARMATURE')
        modifier.object = skel_obj
        modifier.use_bone_envelopes = False
        modifier.use_vertex_groups = True

    # Update the scene
    bpy.context.view_layer.update()

    # Reset the view mode
    bpy.ops.object.mode_set(mode='OBJECT')
    return True
