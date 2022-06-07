
import bpy
from ..lib.driver_utils import driver_find

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
