
import bpy
from ..lib.curve_mapping import nodetree_node_ensure
from ..lib.idprop_utils import idprop_ensure

def setup_combination_shape_keys():
    keys = bpy.data.shape_keys
    if keys:
        for key in keys:
            if key.is_property_set("combination_shape_keys"):
                for item in key.combination_shape_keys:
                    curve = item.falloff
                    nodetree_node_ensure(curve.node_identifier, curve)
                    idprop_ensure(key.user, item.weight_property_name)
                    idprop_ensure(key.user, item.influence_property_name)

def try_setup_combination_shape_keys():
    try:
        setup_combination_shape_keys()
    except AttributeError: pass
