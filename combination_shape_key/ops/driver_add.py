
from typing import Set, TYPE_CHECKING
from string import ascii_letters
from itertools import islice, product
from bpy.types import Operator
from bpy.props import CollectionProperty, StringProperty
from ..lib.driver_utils import driver_find
from ..api.combination_shape_key_target import CombinationShapeKeyTarget
from .base import COMPAT_ENGINES, COMPAT_OBJECTS
if TYPE_CHECKING:
    from bpy.types import Context, Event

class CombinationShapeKeyDriverAdd(Operator):
    bl_idname = 'combination_shape_key.driver_add'
    bl_label = "Add Driver"
    bl_description = "Add a driver for the combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    name: StringProperty(
        name="Name",
        description="Shape key to be used as a driver",
        default="",
        options=set()
        )

    shapes: CollectionProperty(
        name="Drivers",
        type=CombinationShapeKeyTarget,
        options=set()
        )

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        return (context.engine in COMPAT_ENGINES
                and context.object is not None
                and context.object.type in COMPAT_OBJECTS
                and context.object.active_shape_key is not None
                and context.object.data.shape_keys.use_relative
                and context.object.active_shape_key != context.object.data.shape_keys.reference_key
                and context.object.data.shape_keys.is_property_set("combination_shape_keys")
                and context.object.active_shape_key.name in context.object.data.shape_keys.combination_shape_keys)

    def invoke(self, context: 'Context', _: 'Event') -> Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data
        ignore = [key.reference_key.name, shape.name]
        
        for variable in driver_find(key, f'key_blocks["{shape.name}"].value').driver.variables[1:]:
            ignore.append(variable.targets[0].data_path[12:-8])

        shapes = self.shapes
        shapes.clear()

        for name in key.key_blocks.keys():
            if name not in ignore:
                shapes.add()["name"] = name

        self.name = ""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, _: 'Context') -> None:
        layout = self.layout
        layout.activate_init = True
        layout.prop_search(self, "name", self, "shapes", text="", icon='SHAPEKEY_DATA')

    def execute(self, context: 'Context') -> Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data
        target = key.key_blocks.get(self.name)
        manager = key.combination_shape_keys.get(shape.name)

        if target and manager:
            variables = driver_find(key, f'key_blocks["{shape.name}"].value').driver.variables
            variable = variables.new()
            
            chars = ascii_letters
            names = islice(product(chars, repeat=len(variables)//len(chars)+1), len(variables))

            variable.type = 'SINGLE_PROP'
            variable.name = "".join(tuple(names)[len(variables)-1])
            variable.targets[0].id_type = 'KEY'
            variable.targets[0].id = key
            variable.targets[0].data_path = f'key_blocks["{target.name}"].value'

            manager.update()

        return {'FINISHED'}