
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from ..lib.driver_utils import driver_remove
from .base import COMPAT_ENGINES, COMPAT_OBJECTS
if TYPE_CHECKING:
    from bpy.types import Context


class CombinationShapeKeyDriversRemove(Operator):
    bl_idname = 'combination_shape_key.drivers_remove'
    bl_label = "Remove Combination Shape Key Drivers"
    bl_description = "Remove drivers for the combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    return (key.is_property_set("combination_shape_keys")
                            and shape.name in key.combination_shape_keys)
        return False

    def execute(self, context: 'Context') -> Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data
        driver_remove(key, f'key_blocks["{shape.name}"].value')
        collection = key.combination_shape_keys
        collection.remove(collection.find(shape.name))
        return {'FINISHED'}
