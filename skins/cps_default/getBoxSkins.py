## Script (Python) "getBoxSkins"
##parameters=default=0
# $Id$
"""Return available box skin."""

items = [
    {'macro_path': 'here/box_lib/macros/box',
     'title': 'description_box_skin_box', },
    {'macro_path': 'here/box_lib/macros/mmcbox',
     'title': 'description_box_skin_mmcbox', },
    {'macro_path': 'here/box_lib/macros/mmbox',
     'title': 'description_box_skin_mmbox', },
    {'macro_path': 'here/box_lib/macros/sbox',
     'title': 'description_box_skin_sbox', },
    {'macro_path': 'here/box_lib/macros/wbox',
     'title': 'description_box_skin_wbox', },
    ]

if default:
    return items[0]

return items
