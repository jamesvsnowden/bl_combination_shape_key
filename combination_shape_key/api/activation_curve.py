
from bpy.types import PropertyGroup
from ..lib.curve_mapping import BCLMAP_CurveManager

class CombinationShapeKeyActivationCurve(BCLMAP_CurveManager, PropertyGroup):

    def update(self) -> None:
        super().update()
        self.id_data.path_resolve(self.path_from_id().rpartition(".")[0]).fcurve_update()
