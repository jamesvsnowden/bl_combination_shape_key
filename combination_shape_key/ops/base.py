
from typing import Optional, Sequence, TYPE_CHECKING
from itertools import islice, product
from operator import attrgetter
from string import ascii_letters
from uuid import uuid4
from bpy.types import Curve, Lattice
from bpy.props import CollectionProperty, IntProperty
from ..lib.idprop_utils import idprop_create
from ..lib.driver_utils import driver_ensure
from ..api.combination_shape_key_target import CombinationShapeKeyTarget
if TYPE_CHECKING:
    from bpy.types import Key, ShapeKey

COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
COMPAT_OBJECTS = {'MESH', 'LATTICE', 'CURVE'}


class CombinationShapeKeyCreate:

    active_index: IntProperty(
        name="Driver",
        min=0,
        default=0,
        options={'HIDDEN'}
        )

    shapes: CollectionProperty(
        name="Shapes",
        type=CombinationShapeKeyTarget,
        options=set()
        )

    def invoke_internal(self, key: 'Key', exclude: Optional[Sequence['ShapeKey']]=None) -> None:
        shapes = self.shapes
        shapes.clear()
        for shape in key.key_blocks[1:]:
            if exclude is None or shape not in exclude:
                shapes.add()["name"] = shape.name
        self.active_index = 0

    def execute_internal(self, target: 'ShapeKey'):
        key = target.id_data

        manager = key.combination_shape_keys.add()
        manager["name"] = target.name
        manager["identifier"] = f'combination_{uuid4().hex}'
        manager.activation_curve.__init__()

        idprop_create(key.user, manager.weight_property_name)
        idprop_create(key.user, manager.influence_property_name)

        fcurve = driver_ensure(key, f'key_blocks["{target.name}"].value')
        driver = fcurve.driver

        v = driver.variables.new()
        v.type = 'SINGLE_PROP'
        v.name = manager["identifier"]
        v.targets[0].id_type = 'KEY'
        v.targets[0].id = key
        v.targets[0].data_path = 'reference_key.value'

        w = driver.variables.new()
        i = driver.variables.new()
        w.type = 'SINGLE_PROP'
        i.type = 'SINGLE_PROP'
        w.name = "w_"
        i.name = "i_"

        id = key.user
        if isinstance(id, Lattice):
            w.targets[0].id_type = 'LATTICE'
            i.targets[0].id_type = 'LATTICE'
        elif isinstance(id, Curve):
            w.targets[0].id_type = 'CURVE'
            i.targets[0].id_type = 'CURVE'
        else:
            w.targets[0].id_type = 'MESH'
            i.targets[0].id_type = 'MESH'

        w.targets[0].id = id
        i.targets[0].id = id
        w.targets[0].data_path = manager.weight_property_path
        i.targets[0].data_path = manager.influence_property_path

        items = tuple(filter(attrgetter("is_selected"), self.shapes))
        chars = ascii_letters
        names = islice(product(chars, repeat=len(items)//len(chars)+1), len(items))

        for item, name in zip(items, names):
            v = driver.variables.new()
            v.type = 'SINGLE_PROP'
            v.name = "".join(name)
            v.targets[0].id_type = 'KEY'
            v.targets[0].id = key
            v.targets[0].data_path = f'key_blocks["{item.name}"].value'

        manager.update()