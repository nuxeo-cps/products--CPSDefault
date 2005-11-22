##parameters=sort_by=None, direction=None, hide_folder=False, displayed=None
# $Id$
"""
Get a sorted list of contents object
"""
from Products.CPSDefault.utils import filterContents

if not sort_by:
    # Get sort from the session display params
    disp_params = context.REQUEST.SESSION.get('cps_display_params', {})
    sort_by = disp_params.get('sort_by', None)
    direction = disp_params.get('direction', None)

return filterContents(context, context.objectValues(),
                      sort_on=sort_by, sort_order=direction,
                      hide_folder=hide_folder, filter_ptypes=displayed)
