
from bpy.types import AddonPreferences
from ..lib.update import AddonUpdatePreferences

class InBetweenPreferences(AddonUpdatePreferences, AddonPreferences):
    bl_idname = "combination_shape_key"
