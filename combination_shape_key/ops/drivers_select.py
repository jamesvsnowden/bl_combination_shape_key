
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from .base import CombinationShapeKeyCreate, COMPAT_ENGINES, COMPAT_OBJECTS
from ..gui.target_list import CombinationShapeKeyTargetList
if TYPE_CHECKING:
    from bpy.types import Context, Event


class CombinationShapeKeyDriversSelect(CombinationShapeKeyCreate, Operator):
    bl_idname = 'combination_shape_key.drivers_select'
    bl_label = "Select Combination Shape Key Drivers"
    bl_description = "Select drivers for a combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    return (not key.is_property_set("combination_shape_keys")
                            or shape.name not in key.combination_shape_keys)
        return False

    def invoke(self, context: 'Context', event: 'Event') -> Set[str]:
        self.invoke_internal(context.object.data.shape_keys, exclude=(context.object.active_shape_key,))
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context: 'Context') -> None:
        self.layout.template_list(CombinationShapeKeyTargetList.bl_idname, "",
                                  self, "shapes",
                                  self, "active_index")

    def execute(self, context: 'Context') -> Set[str]:
        self.execute_internal(context.object.active_shape_key)
        return {'FINISHED'}
