
from bpy.types import PropertyGroup
from bpy.props import BoolProperty

class CombinationShapeKeyTarget(PropertyGroup):
    """Shape key target"""

    is_selected: BoolProperty(
        name="Selected",
        description="Select the shape key for use",
        default=False,
        options=set()
        )
