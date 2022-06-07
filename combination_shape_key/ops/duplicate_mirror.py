
from typing import Set, TYPE_CHECKING
from uuid import uuid4
from bpy.types import Operator
from ..lib.driver_utils import driver_ensure, driver_find
from ..lib.symmetry import symmetrical_target
from ..lib.idprop_utils import idprop_create
from .base import COMPAT_ENGINES, COMPAT_OBJECTS
if TYPE_CHECKING:
    from bpy.types import Context


class CombinationShapeKeyDuplicateMirror(Operator):

    bl_idname = "combination_shape_key.duplicate_mirror"
    bl_label = "Duplicate & Mirror Combination Shape Key"
    bl_description = "Duplicate and mirror combination shape key and drivers"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    if key.is_property_set("combination_shape_keys"):
                        name = shape.name
                        if (name in key.combination_shape_keys
                            and driver_find(key, f'key_blocks["{shape.name}"].value') is not None
                            ):
                            name = symmetrical_target(name)
                            return bool(name) and name not in key.combination_shape_keys
        return False

    def execute(self, context: 'Context') -> Set[str]:
        object = context.object
        orig = object.active_shape_key
        copy = object.shape_key_add(name=symmetrical_target(orig.name), from_mix=False)

        for src, tgt in zip(orig.data.vertices, copy.data.vertices):
            src_co = src.co
            tgt_co = tgt.co
            src_co.x = tgt_co.x * -1.0
            src_co.y = tgt_co.y
            src_co.z = tgt_co.z

        key = orig.id_data

        manager = key.combination_shape_keys.add()
        manager["name"] = copy.name
        manager["identifier"] = f'combination_{uuid4().hex}'
        manager.activation_curve.__init__()

        idprop_create(key.user, manager.weight_property_name)
        idprop_create(key.user, manager.influence_property_name)

        o_fcurve = driver_find(key, f'key_blocks["{orig.name}"].value') is not None
        o_driver = o_fcurve.driver

        m_fcurve = driver_ensure(key, f'key_blocks["{copy.name}"].value')
        m_driver = m_fcurve.driver

        for o_var in o_driver.variables:
            m_var = m_driver.variables.new()
            m_var = o_var.name
            m_var.type = o_var.type

            for o_tgt, m_tgt in zip(o_var.targets, m_var.targets):
                m_tgt.id_type = o_tgt.id_type
                m_tgt.id = o_tgt.id
                o_name = o_tgt.data_path[12:-8]
                m_name = symmetrical_target(o_name)
                m_tgt.data_path = f'key_blocks["{m_name if m_name in key.key_blocks else o_name}"].value'

        m_driver.type = o_driver.type
        m_driver.expression = o_driver.expression

        return {'FINISHED'}