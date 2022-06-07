
from typing import TYPE_CHECKING
from bpy.types import UIList
if TYPE_CHECKING:
    from bpy.types import Context, UILayout
    from ..api.combination_shape_key_target import CombinationShapeKeyTarget

class CombinationShapeKeyTargetList(UIList):

    bl_idname = 'DATA_UL_combination_shape_key_targets'

    def draw_item(self,
                  context: 'Context',
                  layout: 'UILayout', _1,
                  item: 'CombinationShapeKeyTarget', _2, _3, _4, _5, _6) -> None:
        row = layout.row()
        row.emboss = 'NONE_OR_STATUS'
        row.label(icon='SHAPEKEY_DATA', text=item.name)

        row = row.row()
        row.alignment = 'RIGHT'
        row.prop(context.object.data.shape_keys.key_blocks[item.name], "value", text="")
        row.prop(item, "is_selected",
                 text="",
                 icon=f'CHECKBOX_{"" if item.is_selected else "DE"}HLT',
                 emboss=False)
