
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from bpy.props import IntProperty
from ..lib.driver_utils import driver_find
from .base import COMPAT_ENGINES, COMPAT_OBJECTS
if TYPE_CHECKING:
    from bpy.types import Context


class CombinationShapeKeyDriverRemove(Operator):
    bl_idname = 'combination_shape_key.driver_remove'
    bl_label = "Remove Driver"
    bl_description = "Remove selected driver from the combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(
        name="Index",
        description="The index of the shape key driver variable to remove",
        default=0,
        options=set()
        )

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    if key.is_property_set("combination_shape_keys"):
                        data = key.combination_shape_keys.get(shape.name)
                        if data is not None:
                            fcurve = driver_find(key, f'key_blocks["{shape.name}"].value')
                            return fcurve is not None

    def execute(self, context: 'Context') -> Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data

        fcurve = driver_find(key, f'key_blocks["{shape.name}"].value')
        if fcurve is None:
            self.report({'ERROR'}, "")
            return {'CANCELLED'}

        driver = getattr(fcurve, "driver", None)
        if driver is None:
            self.report({'ERROR'}, "")
            return {'CANCELLED'}

        variables = driver.variables

        index = self.index
        if index >= len(variables):
            self.report({'ERROR'}, f'variable index {index} is out of range.')
            return {'CANCELLED'}

        target = variables[index].targets[0]

        if not target.data_path.startswith('key_blocks['):
            self.report({'ERROR'}, f'invalid variable index {index}')
            return {'CANCELLED'}

        settings = key.combination_shape_keys.get(shape.name)
        if settings is None:
            self.report({'ERROR'}, "")
            return {'CANCELLED'}

        variables.remove(variables[index])
        settings.driver_update()
        return {'FINISHED'}
