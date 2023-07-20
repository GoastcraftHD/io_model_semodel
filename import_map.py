import bpy

# From C2M Importer by Sheilan
def createTextureBlendGroup():
    # Create a group
    node_group = bpy.data.node_groups.new("BlendTextures", 'ShaderNodeTree')
    # Create input & output nodes
    group_outputs = node_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (500,0)
    group_inputs = node_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-1000,0)
    # Add outputs
    node_group.outputs.new('NodeSocketColor','Base Color')
    node_group.outputs.new('NodeSocketColor','Normal')
    node_group.outputs.new('NodeSocketColor','Specular')
    node_group.outputs.new('NodeSocketColor','Roughness')
    # Add inputs
    node_group.inputs.new('NodeSocketColor','Base Color_1')
    node_group.inputs.new('NodeSocketColor','Base Color_2')
    node_group.inputs.new('NodeSocketColor','Normal_1')
    node_group.inputs['Normal_1'].default_value = [0.5, 0.5, 1.0, 1.0]
    node_group.inputs.new('NodeSocketColor','Normal_2')
    node_group.inputs['Normal_2'].default_value = [0.5, 0.5, 1.0, 1.0]
    node_group.inputs.new('NodeSocketColor','Specular_1')
    node_group.inputs['Specular_1'].default_value = [0.5, 0.5, 0.5, 1.0]
    node_group.inputs.new('NodeSocketColor','Specular_2')
    node_group.inputs['Specular_2'].default_value = [0.5, 0.5, 0.5, 1.0]
    node_group.inputs.new('NodeSocketColor','Roughness_1')
    node_group.inputs['Roughness_1'].default_value = [0.5, 0.5, 0.5, 1.0]
    node_group.inputs.new('NodeSocketColor','Roughness_2')
    node_group.inputs['Roughness_2'].default_value = [0.5, 0.5, 0.5, 1.0]
    node_group.inputs.new('NodeSocketColor','Vertex Alpha')
    node_group.inputs.new('NodeSocketFloat','Alpha')
    node_group.inputs['Alpha'].default_value = 1.0
    # Multiply node for alpha + vertex color
    node_multiply1 = node_group.nodes.new('ShaderNodeMath')
    node_multiply1.operation = "MULTIPLY"
    node_multiply1.location = (-800, 0)
    node_multiply1.inputs[1].default_value = 3.0
    node_multiply2 = node_group.nodes.new('ShaderNodeMath')
    node_multiply2.operation = "MULTIPLY"
    node_multiply2.location = (-600, 0)
    node_group.links.new(group_inputs.outputs['Vertex Alpha'], node_multiply1.inputs[0])
    node_group.links.new(node_multiply1.outputs[0], node_multiply2.inputs[0])
    node_group.links.new(group_inputs.outputs['Alpha'], node_multiply2.inputs[1])
    node_clamp = node_group.nodes.new('ShaderNodeClamp')
    node_clamp.location = (-400, 0)
    node_group.links.new(node_multiply2.outputs[0], node_clamp.inputs[0])
    # Color MIX
    mix_color = node_group.nodes.new('ShaderNodeMixRGB')
    mix_color.location = (0, 0)
    mix_color.label = "MixCOLOR"
    node_group.links.new(group_inputs.outputs['Base Color_1'], mix_color.inputs['Color1'])
    node_group.links.new(group_inputs.outputs['Base Color_2'], mix_color.inputs['Color2'])
    node_group.links.new(node_clamp.outputs[0], mix_color.inputs[0])
    node_group.links.new(mix_color.outputs[0], group_outputs.inputs['Base Color'])
    # Normal MIX
    mix_normal = node_group.nodes.new('ShaderNodeMixRGB')
    mix_normal.location = (0, -200)
    mix_normal.label = "MixNORMAL"
    node_group.links.new(group_inputs.outputs['Normal_1'], mix_normal.inputs['Color1'])
    node_group.links.new(group_inputs.outputs['Normal_2'], mix_normal.inputs['Color2'])
    node_group.links.new(node_clamp.outputs[0], mix_normal.inputs[0])
    node_group.links.new(mix_normal.outputs[0], group_outputs.inputs['Normal'])
    # Specular MIX
    mix_specular = node_group.nodes.new('ShaderNodeMixRGB')
    mix_specular.location = (0, -400)
    mix_specular.label = "MixSPECULAR"
    node_group.links.new(group_inputs.outputs['Specular_1'], mix_specular.inputs['Color1'])
    node_group.links.new(group_inputs.outputs['Specular_2'], mix_specular.inputs['Color2'])
    node_group.links.new(node_clamp.outputs[0], mix_specular.inputs[0])
    node_group.links.new(mix_specular.outputs[0], group_outputs.inputs['Specular'])
    # Roughness MIX
    mix_roughness = node_group.nodes.new('ShaderNodeMixRGB')
    mix_roughness.location = (0, -600)
    mix_roughness.label = "MixROUGHNESS"
    node_group.links.new(group_inputs.outputs['Roughness_1'], mix_roughness.inputs['Color1'])
    node_group.links.new(group_inputs.outputs['Roughness_2'], mix_roughness.inputs['Color2'])
    node_group.links.new(node_clamp.outputs[0], mix_roughness.inputs[0])
    node_group.links.new(mix_roughness.outputs[0], group_outputs.inputs['Roughness'])

def load(self, context, filepath=""):
    from . import import_semodel
    createTextureBlendGroup()
    result = import_semodel.load(self, context, filepath, True)

    return result