## Script (Python) "getFolderContents"
##parameters=sort_by=None, direction=None, hide_folder=0
# $Id$
"""
Get a sorted list of contents object
"""
if not sort_by:
    disp_params = context.REQUEST.SESSION.get('cps_display_params', {})
    sort_by    = disp_params.get('sort_by', 'title');
    direction  = disp_params.get('direction', 'default');
elif not direction:
    direction = 'asc'

return context.filterContents(items=context.objectValues(),
                              sort_by=sort_by, direction=direction,
                              hide_folder=hide_folder)
