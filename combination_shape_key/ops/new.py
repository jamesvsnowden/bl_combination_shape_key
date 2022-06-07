
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from bpy.props import StringProperty
from .base import CombinationShapeKeyCreate, COMPAT_ENGINES, COMPAT_OBJECTS
from ..gui.utils import layout_split
from ..gui.target_list import CombinationShapeKeyTargetList
if TYPE_CHECKING:
    from bpy.types import Context, Event


class CombinationShapeKeyNew(CombinationShapeKeyCreate, Operator):
    bl_idname = 'combination_shape_key.new'
    bl_label = "New Combination Shape Key"
    bl_description = "Create a new combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    name: StringProperty(
        name="Name",
        description="Unique name of the combination shape key",
        default="Key",
        options=set()
        )

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                key = object.data.shape_keys
                return key is not None and key.use_relative
        return False

    def invoke(self, context: 'Context', _: 'Event') -> Set[str]:
        self.invoke_internal(context.object.data.shape_keys)
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context: 'Context') -> None:
        layout = self.layout
        layout.separator()
        layout.template_list(CombinationShapeKeyTargetList.bl_idname, "",
                             self, "shapes",
                             self, "active_index")
        layout_split(layout, "Name",
                     factor=0.25,
                     decorate=False).prop(self, "name", text="")
        layout.separator()

    def execute(self, context: 'Context') -> Set[str]:
        object = context.object
        target = object.shape_key_add(name=self.name, from_mix=False)
        self.execute_internal(target)
        object.active_shape_key_index = target.id_data.key_blocks.find(target.name)
        return {'FINISHED'}