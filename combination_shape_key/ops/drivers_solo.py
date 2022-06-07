
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from ..lib.driver_utils import driver_find
from .base import COMPAT_ENGINES, COMPAT_OBJECTS
if TYPE_CHECKING:
    from bpy.types import Context


class CombinationShapeKeyDriversSolo(Operator):
    bl_idname = 'combination_shape_key.drivers_solo'
    bl_label = "Solo Combination Shape Key Drivers"
    bl_description = "Unmutes shape key drivers, sets their values to 1.0 and selects the combination shape key"
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
                            and shape.name in key.combination_shape_keys
                            and driver_find(key, f'key_blocks["{shape.name}"].value') is not None)
        return False

    def execute(self, context: 'Context') -> Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data

        names = [shape.name]
        for variable in driver_find(key, f'key_blocks["{shape.name}"].value').driver.variables[2:]:
            names.append(variable.targets[0].data_path[12:-8])

        for item in key.key_blocks[1:]:
            name = item.name
            if name in names:
                item.mute = False
                item.value = 1.0
            else:
                item.mute = True

        return {'FINISHED'}
