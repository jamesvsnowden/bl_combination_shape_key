
from typing import Optional, TYPE_CHECKING
from bpy.types import PropertyGroup
from bpy.props import (BoolProperty,
                       EnumProperty,
                       FloatProperty,
                       IntProperty,
                       PointerProperty,
                       StringProperty)
from ..lib.curve_mapping import to_bezier, keyframe_points_assign, BLCMAP_Curve
from ..lib.driver_utils import driver_ensure
from ..lib.idprop_utils import idprop_ensure
from .activation_curve import CombinationShapeKeyActivationCurve
if TYPE_CHECKING:
    from bpy.types import Context


class CombinationShapeKey(PropertyGroup):
    """Manages and stores settings for a combination shape key"""

    def fcurve_update(self, _: Optional['Context']=None) -> None:
        """Updates the combination shape key fcurve keyframes"""
        if self.is_valid:
            fcurve = driver_ensure(self.id_data, self.data_path)
            acurve: BLCMAP_Curve = self.activation_curve.curve

            bezier = to_bezier(acurve.points,
                               x_range=(1.0-self.radius, 1.0),
                               y_range=(0.0, self.target_value),
                               extrapolate=not self.clamp)

            keyframe_points_assign(fcurve.keyframe_points, bezier)

    def driver_update(self, _: Optional['Context']=None) -> None:
        """Updates the combination shape key driver"""

        if self.is_valid:
            fc = driver_ensure(self.id_data, self.data_path)
            dr = fc.driver
            dr.type = 'SCRIPTED'
            fc.mute = self.mute

            keys = tuple(var.name for var in dr.variables[3:])

            if len(keys) == 0:
                dr.expression = "0.0"
            else:
                mode = self.mode

                w = dr.variables[1]
                i = dr.variables[2]

                if mode == 'MULTIPLY':
                    dr.expression = f'{w.name}*{i.name}*{"*".join(keys)}'
                elif mode == 'MIN':
                    dr.expression = f'{w.name}*{i.name}*min({",".join(keys)})'
                elif mode == 'MAX':
                    dr.expression = f'{w.name}*{i.name}*max({",".join(keys)})'
                else:
                    dr.expression = f'{w.name}*{i.name}*(({"+".join(keys)})/{str(float(len(keys)))})'

    def id_properties_create(self) -> None:
        """
        Ensures required id-properties exist
        """
        idprop_ensure(self.id_data.user, self.weight_property_name)
        idprop_ensure(self.id_data.user, self.influence_property_name)

    def update(self, context: Optional['Context']=None) -> None:
        """
        Ensures id-properties exist and updates the fcurve and driver for the combination shape key
        """
        self.id_properties_create()
        self.fcurve_update()
        self.driver_update()

    active_driver_index: IntProperty(
        name="Combination Shape Key Driver",
        description="The index of the driver currently selected in the UI",
        min=2,
        default=2,
        options={'HIDDEN'}
        )

    clamp: BoolProperty(
        name="Clamp",
        description="Limits the driven target value to be between 0 and the defined target value",
        default=True,
        options=set(),
        update=fcurve_update
        )

    @property
    def data_path(self) -> str:
        """The path to the target shape key's value property"""
        name = self.name
        return f'key_blocks["{self.name}"].value' if name else ""

    activation_curve: PointerProperty(
        name="Activation Curve",
        description="Activation curve settings",
        type=CombinationShapeKeyActivationCurve,
        options=set()
        )

    identifier: StringProperty(
        name="Shape",
        description="Unique identifier used to hold a reference to the target shape key.",
        get=lambda self: self.get("identifier", ""),
        options={'HIDDEN'}
        )

    @property
    def influence_property_name(self) -> str:
        return f'influence_{self.identifier}'

    @property
    def influence_property_path(self) -> str:
        return f'["{self.influence_property_name}"]'

    @property
    def is_valid(self) -> bool:
        """Whether or not a target shape key exists for the combination shape key"""
        return self.name in self.id_data.key_blocks

    mode: EnumProperty(
        name="Mode",
        description="The method to use when calculating the combination shape key's value",
        items=[
            ('MULTIPLY', "Multiply", "Multiply the driver values"          , 'NONE', 0),
            ('MIN'     , "Lowest"  , "Use the lowest driver value"         , 'NONE', 1),
            ('MAX'     , "Highest" , "Use the highest driver value"        , 'NONE', 2),
            ('AVERAGE' , "Average" , "Use the average of the driver values", 'NONE', 3),
            ],
        default='MULTIPLY',
        options=set(),
        update=driver_update
        )

    mute: BoolProperty(
        name="Mute",
        description=("Whether or not the combination shape key's driver is enabled. Disabling "
                     "the driver allows (temporary) editing of the shape key's value in the UI"),
        default=False,
        options=set(),
        update=driver_update
        )

    radius: FloatProperty(
        name="Radius",
        description=("The distance from the target shape key's value at which to begin "
                     "interpolating the shape key's value"),
        min=0.0,
        max=1.0,
        default=1.0,
        precision=3,
        options=set(),
        update=fcurve_update
        )

    target_value: FloatProperty(
        name="Goal",
        description=("The target value for the combination shape key when all driver shape keys "
                     "are fully activated"),
        min=0.0,
        max=10.0,
        default=1.0,
        precision=3,
        options=set(),
        update=fcurve_update
        )

    @property
    def weight_property_name(self) -> str:
        return f'weight_{self.identifier}'

    @property
    def weight_property_path(self) -> str:
        return f'["{self.weight_property_name}"]'
