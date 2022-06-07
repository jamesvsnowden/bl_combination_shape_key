
from typing import Optional, Tuple, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from bpy.types import UILayout

def layout_split(layout: 'UILayout',
                 label: Optional[str]="",
                 align: Optional[bool]=False,
                 factor: Optional[float]=0.385,
                 decorate: Optional[bool]=True,
                 decorate_fill: Optional[bool]=True
                 ) -> Union['UILayout', Tuple['UILayout', ...]]:
    split = layout.row().split(factor=factor)
    col_a = split.column(align=align)
    col_a.alignment = 'RIGHT'
    if label:
        col_a.label(text=label)
    row = split.row()
    col_b = row.column(align=align)
    if decorate:
        col_c = row.column(align=align)
        col_c.scale_x = 0.8
        if decorate_fill:
            col_c.label(icon='BLANK1')
        else:
            return (col_b, col_c) if label else (col_a, col_b, col_c)
    return col_b if label else (col_a, col_b)
