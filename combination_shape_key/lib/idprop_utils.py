
from typing import Union, TYPE_CHECKING
from rna_prop_ui import rna_idprop_ui_create
import bpy
if TYPE_CHECKING:
    from bpy.types import ID, PoseBone, Bone

def idprop_ensure(owner: Union['ID', 'PoseBone', 'Bone'], name: str) -> None:
    if owner.get(name) is None:
        idprop_create(owner, name)


def idprop_create(owner: Union['ID', 'PoseBone', 'Bone'], name: str) -> None:
    rna_idprop_ui_create(owner, name, default=1.0, min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)


def idprop_remove(owner: Union['ID', 'PoseBone', 'Bone'], name: str) -> None:
    try:
        del owner[name]
    except KeyError: pass
    if bpy.app.version[0] < 3:
        try:
            del owner["_RNA_UI"][name]
        except KeyError: pass