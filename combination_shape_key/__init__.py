# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Combination Shape Keys",
    "description": "Combination shape keys.",
    "author": "James Snowden",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D",
    "warning": "",
    "doc_url": "https://jamesvsnowden.xyz/addons/asks/combination/docs",
    "tracker_url": "https://github.com/jamesvsnowden/bl_combination_shape_key/issues",
    "category": "Animation",
}

UPDATE_URL = ""

import bpy
from .lib.curve_mapping import (BLCMAP_CurvePointProperties,
                                BLCMAP_CurveProperties,
                                BLCMAP_CurvePoint,
                                BLCMAP_CurvePoints,
                                BLCMAP_Curve,
                                BLCMAP_OT_curve_copy,
                                BLCMAP_OT_curve_paste,
                                BLCMAP_OT_handle_type_set,
                                BLCMAP_OT_node_ensure,
                                BCLMAP_OT_curve_point_remove)
from .api.activation_curve import CombinationShapeKeyActivationCurve
from .api.combination_shape_key import CombinationShapeKey
from .api.combination_shape_key_target import CombinationShapeKeyTarget
from .ops.new import CombinationShapeKeyNew
from .ops.drivers_select import CombinationShapeKeyDriversSelect
from .ops.duplicate_mirror import CombinationShapeKeyDuplicateMirror
from .ops.drivers_remove import CombinationShapeKeyDriversRemove
from .ops.drivers_solo import CombinationShapeKeyDriversSolo
from .ops.driver_add import CombinationShapeKeyDriverAdd
from .ops.driver_remove import CombinationShapeKeyDriverRemove
from .gui.target_list import CombinationShapeKeyTargetList
from .gui.settings import CombinationShapeKeySettings
from .gui.menu import draw_menu_items
from .app.bus import MESSAGE_BROKER, shape_key_name_callback
from .app.setup import try_setup_combination_shape_keys, setup_combination_shape_keys


def classes():
    return [
        BLCMAP_CurvePointProperties,
        BLCMAP_CurveProperties,
        BLCMAP_CurvePoint,
        BLCMAP_CurvePoints,
        BLCMAP_Curve,
        BLCMAP_OT_curve_copy,
        BLCMAP_OT_curve_paste,
        BLCMAP_OT_handle_type_set,
        BLCMAP_OT_node_ensure,
        BCLMAP_OT_curve_point_remove,
        CombinationShapeKeyActivationCurve,
        CombinationShapeKey,
        CombinationShapeKeyTarget,
        CombinationShapeKeyNew,
        CombinationShapeKeyDriversSelect,
        CombinationShapeKeyDuplicateMirror,
        CombinationShapeKeyDriversRemove,
        CombinationShapeKeyDriversSolo,
        CombinationShapeKeyDriverAdd,
        CombinationShapeKeyDriverRemove,
        CombinationShapeKeyTargetList,
        CombinationShapeKeySettings,
        ]


@bpy.app.handlers.persistent
def load_post_handler(_=None) -> None:
    bpy.msgbus.clear_by_owner(MESSAGE_BROKER)
    bpy.msgbus.subscribe_rna(key=(bpy.types.ShapeKey, "name"),
                             owner=MESSAGE_BROKER,
                             args=tuple(),
                             notify=shape_key_name_callback)

    # On initial load accessing bpy.data.shape_keys will raise AttributeError.
    # Retry after 5 seconds.
    try:
        setup_combination_shape_keys()
    except AttributeError:
        bpy.app.timers.register(try_setup_combination_shape_keys, first_interval=5)


def register():
    from bpy.utils import register_class
    from bpy.types import Key
    from bpy.props import CollectionProperty

    BLCMAP_OT_curve_copy.bl_idname = "combination_shape_key.curve_copy"
    BLCMAP_OT_curve_paste.bl_idname = "combination_shape_key.curve_paste"
    BLCMAP_OT_node_ensure.bl_idname = "combination_shape_key.node_ensure"
    BCLMAP_OT_curve_point_remove.bl_idname = "combination_shape_key.curve_point_remove"
    BLCMAP_OT_handle_type_set.bl_idname = "combination_shape_key.handle_type_set"

    from .lib import update
    update.register("combination_shape_key", UPDATE_URL)

    for cls in classes():
        register_class(cls)

    Key.combination_shape_keys = CollectionProperty(
        name="Combination Shape Keys",
        type=CombinationShapeKey,
        options=set()
        )

    bpy.types.MESH_MT_shape_key_context_menu.append(draw_menu_items)
    bpy.app.handlers.load_post.append(load_post_handler)
    load_post_handler() # Ensure messages are subscribed to on first install


def unregister():
    import sys
    from operator import itemgetter
    from bpy.types import Key
    from bpy.utils import unregister_class

    bpy.msgbus.clear_by_owner(MESSAGE_BROKER)
    bpy.app.handlers.load_post.remove(load_post_handler)
    bpy.types.MESH_MT_shape_key_context_menu.remove(draw_menu_items)

    from .lib import update
    update.unregister()

    try:
        del Key.combination_shape_keys
    except: pass

    for cls in reversed(classes()):
        unregister_class(cls)

    modules_ = sys.modules 
    modules_ = dict(sorted(modules_.items(), key=itemgetter(0)))
   
    for name in modules_.keys():
        if name.startswith(__name__):
            del sys.modules[name]
