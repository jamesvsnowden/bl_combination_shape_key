
from typing import TYPE_CHECKING
from ..ops.new import CombinationShapeKeyNew
from ..ops.drivers_select import CombinationShapeKeyDriversSelect
from ..ops.duplicate_mirror import CombinationShapeKeyDuplicateMirror
from ..ops.drivers_remove import CombinationShapeKeyDriversRemove
from ..ops.drivers_solo import CombinationShapeKeyDriversSolo
if TYPE_CHECKING:
    from bpy.types import Context, Menu


def draw_menu_items(menu: 'Menu', context: 'Context') -> None:
    object = context.object
    if object is not None:
        layout = menu.layout
        layout.separator()
        layout.operator(CombinationShapeKeyNew.bl_idname,
                        icon='ADD',
                        text="New Combination")

        shape = object.active_shape_key
        if shape is not None:
            key = shape.id_data
            if shape != key.reference_key:
                data = key.combination_shape_keys if key.is_property_set("combination_shape_keys") else None
                name = shape.name
                if data is None or name not in data:
                    layout.operator(CombinationShapeKeyDriversSelect.bl_idname,
                                    icon='ANIM',
                                    text="Select Combination Drivers")
                elif data is not None:
                    layout.operator(CombinationShapeKeyDriversSolo.bl_idname,
                                    icon='ZOOM_SELECTED',
                                    text="Activate Combination")
                    layout.operator(CombinationShapeKeyDuplicateMirror.bl_idname,
                                    icon='MOD_MIRROR',
                                    text="Duplicate & Mirror Combination")
                    layout.operator(CombinationShapeKeyDriversRemove.bl_idname,
                                    icon='REMOVE',
                                    text="Remove Combination Drivers")
