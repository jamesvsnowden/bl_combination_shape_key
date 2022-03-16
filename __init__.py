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
    "blender": (2, 90, 0),
    "location": "View3D",
    "warning": "",
    "doc_url": "https://combination_shape_keys.github.io",
    "tracker_url": "https://github.com/jamesvsnowden/bl_combination_shape_key/issues",
    "category": "Animation",
}

import itertools
import operator
import string
import typing
import uuid
import bpy
from rna_prop_ui import rna_idprop_ui_create
from .lib import curve_mapping
from .lib.driver_utils import driver_ensure, driver_find, driver_remove
from .lib.symmetry import symmetrical_target

curve_mapping.BLCMAP_OT_curve_copy.bl_idname = "csk.curve_copy"
curve_mapping.BLCMAP_OT_curve_paste.bl_idname = "csk.curve_paste"
curve_mapping.BLCMAP_OT_curve_edit.bl_idname = "csk.curve_edit"

def idprop_ensure(owner: typing.Union[bpy.types.ID, bpy.types.PoseBone, bpy.types.Bone], name: str) -> None:
    if owner.get(name) is None:
        idprop_create(owner, name)

def idprop_create(owner: typing.Union[bpy.types.ID, bpy.types.PoseBone, bpy.types.Bone], name: str) -> None:
    rna_idprop_ui_create(owner, name, default=1.0, min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)

def idprop_remove(owner: typing.Union[bpy.types.ID, bpy.types.PoseBone, bpy.types.Bone], name: str) -> None:
    try:
        del owner[name]
    except KeyError: pass
    if bpy.app.version[0] < 3:
        try:
            del owner["_RNA_UI"][name]
        except KeyError: pass

#region Properties
###################################################################################################

class CombinationShapeKeyTargetFalloff(curve_mapping.BCLMAP_CurveManager, bpy.types.PropertyGroup):

    def update(self, context: typing.Optional[bpy.types.Context] = None) -> None:
        super().update(context)
        self.id_data.path_resolve(self.path_from_id().rpartition(".")[0]).fcurve_update()


class CombinationShapeKey(bpy.types.PropertyGroup):
    """Manages and stores settings for a combination shape key"""

    def fcurve_update(self, context: typing.Optional[bpy.types.Context]=None) -> None:
        """Updates the combination shape key fcurve keyframes"""
        if self.is_valid:
            fcurve = driver_ensure(self.id_data, self.data_path)
            dcurve: curve_mapping.BLCMAP_Curve = self.falloff.curve

            bezier = curve_mapping.to_bezier(dcurve.points,
                                             x_range=(1.0-self.radius, 1.0),
                                             y_range=(0.0, self.target_value),
                                             extrapolate=not self.clamp)

            curve_mapping.keyframe_points_assign(fcurve.keyframe_points, bezier)

    def driver_update(self, context: typing.Optional[bpy.types.Context]=None) -> None:
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

    def update(self, context: typing.Optional[bpy.types.Context]=None) -> None:
        """
        Ensures id-properties exist and updates the fcurve and driver for the combination shape key
        """
        self.id_properties_create()
        self.fcurve_update()
        self.driver_update()

    active_driver_index: bpy.props.IntProperty(
        name="Combination Shape Key Driver",
        description="The index of the driver currently selected in the UI",
        min=2,
        default=2,
        options={'HIDDEN'}
        )

    clamp: bpy.props.BoolProperty(
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

    falloff: bpy.props.PointerProperty(
        name="Falloff",
        description="Falloff curve settings",
        type=CombinationShapeKeyTargetFalloff,
        options=set()
        )

    identifier: bpy.props.StringProperty(
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

    mode: bpy.props.EnumProperty(
        name="Mode",
        description="The method to use when calculating the combination shape key's value",
        items=[
            ('MULTIPLY', "Multiply", "Multiply the driver values"                            , 'NONE', 0),
            ('MIN'     , "Lowest"  , "Use the lowest driver value"                           , 'NONE', 1),
            ('MAX'     , "Highest" , "Use the highest driver value"                          , 'NONE', 2),
            ('AVERAGE' , "Average" , "Use the average of the driver values"                  , 'NONE', 3),
            ],
        default='MULTIPLY',
        options=set(),
        update=driver_update
        )

    mute: bpy.props.BoolProperty(
        name="Mute",
        description=("Whether or not the combination shape key's driver is enabled. Disabling "
                     "the driver allows (temporary) editing of the shape key's value in the UI"),
        default=False,
        options=set(),
        update=driver_update
        )

    radius: bpy.props.FloatProperty(
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

    target_value: bpy.props.FloatProperty(
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


class CombinationShapeKeyTarget(bpy.types.PropertyGroup):
    """Shape key target"""

    is_selected: bpy.props.BoolProperty(
        name="Selected",
        description="Select the shape key for use",
        default=False,
        options=set()
        )

#endregion Properties

#region Operators
###################################################################################################

COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
COMPAT_OBJECTS = {'MESH', 'LATTICE', 'CURVE'}


class CombinationShapeKeyCreate:

    active_index: bpy.props.IntProperty(
        name="Driver",
        min=0,
        default=0,
        options={'HIDDEN'}
        )

    shapes: bpy.props.CollectionProperty(
        name="Shapes",
        type=CombinationShapeKeyTarget,
        options=set()
        )

    def invoke_internal(self,
                      key: bpy.types.Key,
                      exclude: typing.Optional[typing.Sequence[bpy.types.ShapeKey]]=None) -> None:
        shapes = self.shapes
        shapes.clear()
        for shape in key.key_blocks[1:]:
            if exclude is None or shape not in exclude:
                shapes.add()["name"] = shape.name
        self.active_index = 0

    def execute_internal(self, target: bpy.types.ShapeKey):
        key = target.id_data

        manager = key.combination_shape_keys.add()
        manager["name"] = target.name
        manager["identifier"] = f'combination_{uuid.uuid4().hex}'
        manager.falloff.__init__()

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
        if isinstance(id, bpy.types.Lattice):
            w.targets[0].id_type = 'LATTICE'
            i.targets[0].id_type = 'LATTICE'
        elif isinstance(id, bpy.types.Curve):
            w.targets[0].id_type = 'CURVE'
            i.targets[0].id_type = 'CURVE'
        else:
            w.targets[0].id_type = 'MESH'
            i.targets[0].id_type = 'MESH'

        w.targets[0].id = id
        i.targets[0].id = id
        w.targets[0].data_path = manager.weight_property_path
        i.targets[0].data_path = manager.influence_property_path

        items = tuple(filter(operator.attrgetter("is_selected"), self.shapes))
        chars = string.ascii_letters
        names = itertools.islice(itertools.product(chars, repeat=len(items)//len(chars)+1), len(items))

        for item, name in zip(items, names):
            v = driver.variables.new()
            v.type = 'SINGLE_PROP'
            v.name = "".join(name)
            v.targets[0].id_type = 'KEY'
            v.targets[0].id = key
            v.targets[0].data_path = f'key_blocks["{item.name}"].value'

        manager.update()


class CombinationShapeKeyNew(CombinationShapeKeyCreate, bpy.types.Operator):
    bl_idname = 'combination_shape_key.new'
    bl_label = "New Combination Shape Key"
    bl_description = "Create a new combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    name: bpy.props.StringProperty(
        name="Name",
        description="Unique name of the combination shape key",
        default="Key",
        options=set()
        )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                key = object.data.shape_keys
                return key is not None and key.use_relative
        return False

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> typing.Set[str]:
        self.invoke_internal(context.object.data.shape_keys)
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.separator()
        layout.template_list(CombinationShapeKeyTargetList.bl_idname, "", self, "shapes", self, "active_index")
        layout_split(layout, "Name", factor=0.25, decorate=False).prop(self, "name", text="")
        layout.separator()


    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        object = context.object
        target = object.shape_key_add(name=self.name, from_mix=False)
        self.execute_internal(target)
        object.active_shape_key_index = target.id_data.key_blocks.find(target.name)
        return {'FINISHED'}


class CombinationShapeKeyDriversSelect(CombinationShapeKeyCreate, bpy.types.Operator):
    bl_idname = 'combination_shape_key.drivers_select'
    bl_label = "Select Combination Shape Key Drivers"
    bl_description = "Select drivers for a combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    return (not key.is_property_set("combination_shape_keys")
                            or shape.name not in key.combination_shape_keys)
        return False

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> typing.Set[str]:
        self.invoke_internal(context.object.data.shape_keys, exclude=(context.object.active_shape_key,))
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context: bpy.types.Context) -> None:
        self.layout.template_list(CombinationShapeKeyTargetList.bl_idname, "", self, "shapes", self, "active_index")

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        self.execute_internal(context.object.active_shape_key)
        return {'FINISHED'}


class CombinationShapeKeyDuplicateMirror(bpy.types.Operator):

    bl_idname = "combination_shape_key.duplicate_mirror"
    bl_label = "Duplicate & Mirror Combination Shape Key"
    bl_description = "Duplicate and mirror combination shape key and drivers"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    if key.is_property_set("combination_shape_keys"):
                        name = shape.name
                        if (name in key.combination_shape_keys
                            and driver_find(key, f'key_blocks["{shape.name}"].value') is not None
                            ):
                            name = symmetrical_target(name)
                            return bool(name) and name not in key.combination_shape_keys
        return False

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        object = context.object
        orig = object.active_shape_key
        copy = object.shape_key_add(name=symmetrical_target(orig.name), from_mix=False)

        for src, tgt in zip(orig.data.vertices, copy.data.vertices):
            src_co = src.co
            tgt_co = tgt.co
            src_co.x = tgt_co.x * -1.0
            src_co.y = tgt_co.y
            src_co.z = tgt_co.z

        key = orig.id_data

        manager = key.combination_shape_keys.add()
        manager["name"] = copy.name
        manager["identifier"] = f'combination_{uuid.uuid4().hex}'
        manager.falloff.__init__()

        idprop_create(key.user, manager.weight_property_name)
        idprop_create(key.user, manager.influence_property_name)

        o_fcurve = driver_find(key, f'key_blocks["{orig.name}"].value') is not None
        o_driver = o_fcurve.driver

        m_fcurve = driver_ensure(key, f'key_blocks["{copy.name}"].value')
        m_driver = m_fcurve.driver

        for o_var in o_driver.variables:
            m_var = m_driver.variables.new()
            m_var = o_var.name
            m_var.type = o_var.type

            for o_tgt, m_tgt in zip(o_var.targets, m_var.targets):
                m_tgt.id_type = o_tgt.id_type
                m_tgt.id = o_tgt.id
                o_name = o_tgt.data_path[12:-8]
                m_name = symmetrical_target(o_name)
                m_tgt.data_path = f'key_blocks["{m_name if m_name in key.key_blocks else o_name}"].value'

        m_driver.type = o_driver.type
        m_driver.expression = o_driver.expression

        return {'FINISHED'}


class CombinationShapeKeyDriversRemove(bpy.types.Operator):
    bl_idname = 'combination_shape_key.drivers_remove'
    bl_label = "Remove Combination Shape Key Drivers"
    bl_description = "Remove drivers for the combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    return (key.is_property_set("combination_shape_keys")
                            and shape.name in key.combination_shape_keys)
        return False

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data
        driver_remove(key, f'key_blocks["{shape.name}"].value')
        collection = key.combination_shape_keys
        collection.remove(collection.find(shape.name))
        return {'FINISHED'}


class CombinationShapeKeyDriversSolo(bpy.types.Operator):
    bl_idname = 'combination_shape_key.drivers_solo'
    bl_label = "Solo Combination Shape Key Drivers"
    bl_description = "Unmutes shape key drivers, sets their values to 1.0 and selects the combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    return (key.is_property_set("combination_shape_keys")
                            and shape.name in key.combination_shape_keys
                            and driver_find(key, f'key_blocks["{shape.name}"].value') is not None)
        return False

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data


        names = [shape.name]
        for variable in driver_find(key, f'key_blocks["{shape.name}"].value').driver.variables[2:]:
            names.append(variable.targets[0].data_path[12:-8])

        for item in key.key_blocks[1:]:
            name = item.name
            if name in names:
                item.mute = False
                item.value = 1.0
            else:
                item.mute = True

        return {'FINISHED'}


class CombinationShapeKeyDriverAdd(bpy.types.Operator):
    bl_idname = 'combination_shape_key.driver_add'
    bl_label = "Add Driver"
    bl_description = "Add a driver for the combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    name: bpy.props.StringProperty(
        name="Name",
        description="Shape key to be used as a driver",
        default="",
        options=set()
        )

    shapes: bpy.props.CollectionProperty(
        name="Drivers",
        type=CombinationShapeKeyTarget,
        options=set()
        )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return (context.engine in COMPAT_ENGINES
                and context.object is not None
                and context.object.type in COMPAT_OBJECTS
                and context.object.active_shape_key is not None
                and context.object.data.shape_keys.use_relative
                and context.object.active_shape_key != context.object.data.shape_keys.reference_key
                and context.object.data.shape_keys.is_property_set("combination_shape_keys")
                and context.object.active_shape_key.name in context.object.data.shape_keys.combination_shape_keys)

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> typing.Set[str]:
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

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.activate_init = True
        layout.prop_search(self, "name", self, "shapes", text="", icon='SHAPEKEY_DATA')

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data
        target = key.key_blocks.get(self.name)
        manager = key.combination_shape_keys.get(shape.name)

        if target and manager:
            variables = driver_find(key, f'key_blocks["{shape.name}"].value').driver.variables
            variable = variables.new()
            
            chars = string.ascii_letters
            names = itertools.islice(itertools.product(chars, repeat=len(variables)//len(chars)+1), len(variables))

            variable.type = 'SINGLE_PROP'
            variable.name = "".join(tuple(names)[len(variables)-1])
            variable.targets[0].id_type = 'KEY'
            variable.targets[0].id = key
            variable.targets[0].data_path = f'key_blocks["{target.name}"].value'

            manager.update()

        return {'FINISHED'}


class CombinationShapeKeyDriverRemove(bpy.types.Operator):
    bl_idname = 'combination_shape_key.driver_remove'
    bl_label = "Remove Driver"
    bl_description = "Remove selected driver from the combination shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    if key.is_property_set("combination_shape_keys"):
                        data = key.combination_shape_keys.get(shape.name)
                        if data is not None:
                            fcurve = driver_find(key, f'key_blocks["{shape.name}"].value')
                            return fcurve is not None and data.active_driver_index < len(fcurve.driver.variables)

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data
        variables = driver_find(key, f'key_blocks["{shape.name}"].value').driver.variables
        data = key.combination_shape_keys[shape.name]
        variables.remove(variables[data.active_driver_index])
        data.active_driver_index = min(data.active_driver_index, len(variables)-1)
        return {'FINISHED'}


class CombinationShapeKeyDriverMoveUp(bpy.types.Operator):
    bl_idname = 'combination_shape_key.driver_move_up'
    bl_label = "Move Up"
    bl_description = "Move the driver up within the list of drivers"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    if key.is_property_set("combination_shape_keys"):
                        data = key.combination_shape_keys.get(shape.name)
                        if data is not None:
                            index = data.active_driver_index
                            if index > 2:
                                fcurve = driver_find(key, f'key_blocks["{shape.name}"].value')
                                return fcurve is not None and index < len(fcurve.driver.variables)
        return False

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data
        variables = driver_find(key, f'key_blocks["{shape.name}"].value').driver.variables
        data = key.combination_shape_keys[shape.name]
        index = data.active_driver_index
        cache = variables[index].targets[0].data_path
        variables[index].targets[0].data_path = variables[index-1].targets[0].data_path
        variables[index-1].targets[0].data_path = cache
        data.active_driver_index -= 1
        return {'FINISHED'}


class CombinationShapeKeyDriverMoveDown(bpy.types.Operator):
    bl_idname = 'combination_shape_key.driver_move_down'
    bl_label = "Move Down"
    bl_description = "Move the driver down within the list of drivers"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    if key.is_property_set("combination_shape_keys"):
                        data = key.combination_shape_keys.get(shape.name)
                        if data is not None:
                            fcurve = driver_find(key, f'key_blocks["{shape.name}"].value')
                            return fcurve is not None and data.active_driver_index < len(fcurve.driver.variables) - 1
        return False

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        shape = context.object.active_shape_key
        key = shape.id_data
        variables = driver_find(key, f'key_blocks["{shape.name}"].value').driver.variables
        data = key.combination_shape_keys[shape.name]
        index = data.active_driver_index
        cache = variables[index].targets[0].data_path
        variables[index].targets[0].data_path = variables[index+1].targets[0].data_path
        variables[index+1].targets[0].data_path = cache
        data.active_driver_index += 1
        return {'FINISHED'}

#endregion Operators

#region User Interface
###################################################################################################

def layout_split(layout: bpy.types.UILayout,
                 label: typing.Optional[str]="",
                 align: typing.Optional[bool]=False,
                 factor: typing.Optional[float]=0.385,
                 decorate: typing.Optional[bool]=True,
                 decorate_fill: typing.Optional[bool]=True
                 ) -> typing.Union[bpy.types.UILayout, typing.Tuple[bpy.types.UILayout, ...]]:
    split = layout.row().split(factor=factor)
    col_a = split.column(align=align)
    col_a.alignment = 'RIGHT'
    if label:
        col_a.label(text=label)
    row = split.row()
    col_b = row.column(align=align)
    if decorate:
        col_c = row.column(align=align)
        if decorate_fill:
            col_c.label(icon='BLANK1')
        else:
            return (col_b, col_c) if label else (col_a, col_b, col_c)
    return col_b if label else (col_a, col_b)

class CombinationShapeKeyDriverList(bpy.types.UIList):

    bl_idname = 'DATA_UL_combination_shape_key_drivers'

    def draw_item(self,
                  context: bpy.types.Context,
                  layout: bpy.types.UILayout,
                  data: bpy.types.ChannelDriverVariables,
                  item: bpy.types.DriverVariable,
                  icon, active_data, active_property, index, fltflag) -> None:

        target = item.targets[0]
        key = target.id
        name = target.data_path[12:-8]
        shape = key.key_blocks.get(name) if isinstance(key, bpy.types.Key) else None

        row = layout.row()
        row.emboss = 'NONE_OR_STATUS'

        subrow = row.row()
        subrow.alert = shape is None
        subrow.label(icon='SHAPEKEY_DATA', text=name)

        if shape is not None:
            subrow = row.row()
            subrow.alignment = 'RIGHT'
            subrow.prop(shape, "value", text="")

    def filter_items(self,
                     context: bpy.types.Context,
                     data: bpy.types.Driver,
                     propname: str) -> typing.Tuple[typing.List, typing.List]:
        # The first variable of the driver is used as an internal reference to the
        # combination shape key manager, so it is filtered out for the purposes of
        # displaying the list of shape key drivers. The index order is kept as is
        # to provide easier lookups on driver variables.
        variables = getattr(data, propname)
        used_item = self.bitflag_filter_item
        res_flags = [used_item if i > 2 else ~used_item for i in range(len(variables))]
        res_order = list(range(len(variables)))
        return res_flags, res_order

class CombinationShapeKeyTargetList(bpy.types.UIList):

    bl_idname = 'DATA_UL_combination_shape_key_targets'

    def draw_item(self,
                  context: bpy.types.Context,
                  layout: bpy.types.UILayout,
                  data: bpy.types.CollectionProperty,
                  item: CombinationShapeKeyTarget,
                  icon, active_data, active_property, index, fltflag) -> None:

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

class CombinationShapeKeySettings(bpy.types.Panel):

    bl_parent_id = "DATA_PT_shape_keys"
    bl_idname = "DATA_PT_combination_shape_key_settings"
    bl_label = "Combination Shape Key Drivers"
    bl_description = "Combination shape key driver settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        object = context.object
        if object is not None:
            shape = object.active_shape_key
            if shape is not None:
                key = shape.id_data
                return (key.is_property_set("combination_shape_keys")
                        and shape.name in key.combination_shape_keys)
        return False

    def draw(self, context: bpy.types.Context) -> None:
        obj = context.object
        key = obj.data.shape_keys

        target = key.combination_shape_keys[obj.active_shape_key.name]
        fcurve = driver_find(key, target.data_path)
        layout = self.layout

        if fcurve:
            row = layout.row()
            col = row.column()
            col.template_list(CombinationShapeKeyDriverList.bl_idname, "",
                              fcurve.driver, "variables",
                              target, "active_driver_index")

            col = row.column(align=True)
            col.operator(CombinationShapeKeyDriverAdd.bl_idname, icon='ADD', text="")
            col.operator(CombinationShapeKeyDriverRemove.bl_idname, icon='REMOVE', text="")
            col.separator()
            col.operator(CombinationShapeKeyDriverMoveUp.bl_idname, icon='TRIA_UP', text="")
            col.operator(CombinationShapeKeyDriverMoveDown.bl_idname, icon='TRIA_DOWN', text="")
        else:
            col = layout_split(layout, " ")
            col.operator(CombinationShapeKeyDriverAdd.bl_idname, icon='ADD', text="Add")

        a, b, c = layout_split(layout, decorate_fill=False)
        a.label(text="Mode")
        a.label(text="Influence")
        b.prop(target, "mode", text="")
        b.prop(target.id_data.user, target.influence_property_path, text="", slider=True)
        c.operator(CombinationShapeKeyDriversSolo.bl_idname, icon='SOLO_OFF', text="")

        row = b.row()
        row.alignment = 'RIGHT'
        row.label(text="Enable Driver")
        row.prop(target, "mute", text="", invert_checkbox=True)

        layout.separator()

        a, b = layout_split(layout)
        a.label(text="Goal")
        a.label(text="Radius")
        b.prop(target, "target_value", text="")
        b.prop(target, "radius", text="", slider=True)

        row = b.row()
        row.alignment = 'RIGHT'
        row.label(text="Clamp Value")
        row.prop(target, "clamp", text="")

        layout.separator()

        col = layout_split(layout, "Easing", decorate=False)
        curve_mapping.draw_curve_manager_ui(col, target.falloff)


def draw_menu_items(menu: bpy.types.Menu, context: bpy.types.Context) -> None:
    object = context.object
    if object is not None:
        layout = menu.layout
        layout.separator()
        layout.operator(CombinationShapeKeyNew.bl_idname,
                        icon='ADD',
                        text="New Combination Shape Key")

        shape = object.active_shape_key
        if shape is not None:
            key = shape.id_data
            if shape != key.reference_key:
                data = key.combination_shape_keys if key.is_property_set("combination_shape_keys") else None
                name = shape.name
                if data is None or name not in data:
                    layout.operator(CombinationShapeKeyDriversSelect.bl_idname,
                                    icon='ANIM',
                                    text="Select Combination Shape Key Drivers")
                elif data is not None:
                    layout.operator(CombinationShapeKeyDuplicateMirror.bl_idname,
                                    icon='MOD_MIRROR',
                                    text="Duplicate & Mirror Combination Shape Key")
                    layout.operator(CombinationShapeKeyDriversRemove.bl_idname,
                                    icon='REMOVE',
                                    text="Remove Combination Shape Key Drivers")


#endregion User Interface

CLASSES = [
    curve_mapping.BLCMAP_CurvePointProperties,
    curve_mapping.BLCMAP_CurveProperties,
    curve_mapping.BLCMAP_CurvePoint,
    curve_mapping.BLCMAP_CurvePoints,
    curve_mapping.BLCMAP_Curve,
    curve_mapping.BLCMAP_OT_curve_copy,
    curve_mapping.BLCMAP_OT_curve_paste,
    curve_mapping.BLCMAP_OT_curve_edit,
    curve_mapping.BLCMAP_OT_node_ensure,
    CombinationShapeKeyTargetFalloff,
    CombinationShapeKey,
    CombinationShapeKeyTarget,
    CombinationShapeKeyNew,
    CombinationShapeKeyDriversSelect,
    CombinationShapeKeyDuplicateMirror,
    CombinationShapeKeyDriversRemove,
    CombinationShapeKeyDriversSolo,
    CombinationShapeKeyDriverAdd,
    CombinationShapeKeyDriverRemove,
    CombinationShapeKeyDriverMoveUp,
    CombinationShapeKeyDriverMoveDown,
    CombinationShapeKeyTargetList,
    CombinationShapeKeyDriverList,
    CombinationShapeKeySettings,
    ]

MESSAGE_BROKER = object()

def shape_key_name_callback():
    for key in bpy.data.shape_keys:
        if key.is_property_set("combination_shape_keys"):
            for shape in key.key_blocks:
                fcurve = driver_find(key, f'key_blocks["{shape.name}"].value')
                if fcurve is not None and len(fcurve.driver.variables):
                    variable = fcurve.driver.variables[0]
                    if variable is not None and variable.type == 'SINGLE_PROP':
                        target = variable.targets[0]
                        if target.id_type == 'KEY' and target.id == key and target.data_path == "reference_key.value":
                            identifier = variable.name
                            manager = next((x for x in key.combination_shape_keys if x.get("identifier", "") == identifier), None)
                            if manager:
                                manager["name"] = shape.name

def setup_combination_shape_keys():
    keys = bpy.data.shape_keys
    if keys:
        for key in keys:
            if key.is_property_set("combination_shape_keys"):
                for item in key.combination_shape_keys:
                    curve = item.falloff
                    curve_mapping.nodetree_node_ensure(curve.node_identifier, curve)
                    idprop_ensure(key.user, item.weight_property_name)
                    idprop_ensure(key.user, item.influence_property_name)

def try_setup_combination_shape_keys():
    try:
        setup_combination_shape_keys()
    except AttributeError: pass

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
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Key.combination_shape_keys = bpy.props.CollectionProperty(
        name="Combination Shape Keys",
        type=CombinationShapeKey,
        options=set()
        )

    bpy.types.MESH_MT_shape_key_context_menu.append(draw_menu_items)
    bpy.app.handlers.load_post.append(load_post_handler)
    load_post_handler() # Ensure messages are subscribed to on first install

def unregister():
    import sys
    import operator

    bpy.msgbus.clear_by_owner(MESSAGE_BROKER)
    bpy.app.handlers.load_post.remove(load_post_handler)
    bpy.types.MESH_MT_shape_key_context_menu.remove(draw_menu_items)

    try:
        del bpy.types.Key.combination_shape_keys
    except: pass

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    modules_ = sys.modules 
    modules_ = dict(sorted(modules_.items(), key=operator.itemgetter(0)))
   
    for name in modules_.keys():
        if name.startswith(__name__):
            del sys.modules[name]
