
from typing import TYPE_CHECKING
from bpy.types import Panel
from ..lib.driver_utils import driver_find
from ..lib.curve_mapping import draw_curve_manager_ui
from ..ops.driver_add import CombinationShapeKeyDriverAdd
from ..ops.driver_remove import CombinationShapeKeyDriverRemove
if TYPE_CHECKING:
    from bpy.types import Context, UILayout

class CombinationShapeKeySettings(Panel):

    bl_parent_id = "DATA_PT_shape_keys"
    bl_idname = "DATA_PT_combination_shape_key_settings"
    bl_label = "Combination"
    bl_description = "Combination shape key settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        object = context.object
        if object is not None:
            shape = object.active_shape_key
            if shape is not None:
                key = shape.id_data
                return (key.is_property_set("combination_shape_keys")
                        and shape.name in key.combination_shape_keys)
        return False

    def section(self, label: str) -> 'UILayout':
        split = self.layout.row().split(factor=0.385)
        labels_column = split.column()
        values_column = split.column()
        labels_column.alignment = 'RIGHT'
        labels_column.label(text=label)
        return values_column

    def draw(self, context: 'Context') -> None:
        object = context.object
        key = object.data.shape_keys
        settings = key.combination_shape_keys[object.active_shape_key.name]

        column = self.section('Combination Of')
        fcurve = driver_find(key, settings.data_path)
        if fcurve:
            for index, variable in enumerate(fcurve.driver.variables):
                target = variable.targets[0]
                if target.data_path.startswith('key_blocks['):
                    name = target.data_path[12:-8]
                    shape = key.key_blocks.get(name)
                    row = column.row(align=True)
                    box = row.box()
                    box.scale_y = 0.5
                    subrow = box.row(align=True)
                    subrow.alert = shape is None
                    subrow.label(icon='SHAPEKEY_DATA', text=name)
                    row.operator(CombinationShapeKeyDriverRemove.bl_idname,
                                 text="",
                                 icon='X').index = index

        subrow = column.row()
        subrow.operator(CombinationShapeKeyDriverAdd.bl_idname,
                        icon='ADD',
                        text="Add")
        subrow.separator(factor=2.0)

        column.separator()

        column = self.section("Mode")
        subrow = column.row()
        subrow.prop(settings, "mode", text="")
        subrow.separator(factor=2.0)

        subrow = column.row()
        subrow.prop(settings.id_data.user,
                    settings.influence_property_path,
                    text="Influence",
                    slider=True)
        subrow.separator(factor=2.0)

        subrow = column.row()
        subrow.alignment = 'RIGHT'
        subrow.label(text="Enable Driver")
        subrow.prop(settings, "mute", text="", invert_checkbox=True)
        subrow.separator(factor=2.0)

        column.separator()

        column = self.section("Activation")
        subrow = column.row()
        column = subrow.column()
        draw_curve_manager_ui(column, settings.activation_curve)
        subrow.separator(factor=2.0)

        column.prop(settings, "radius", text="Radius")
        column.prop(settings, "target_value", text="Target")

        subrow = column.row()
        subrow.alignment = 'RIGHT'
        subrow.label(text="Clamp")
        subrow.prop(settings, "clamp", text="")
