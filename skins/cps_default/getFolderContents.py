## Script (Python) "getFolderContents"
##parameters=sort_by=None, direction=None, hide_folder=0, displayed=['']
# $Id$
"""
Get a sorted list of contents object
"""
if not sort_by:
    disp_params = context.REQUEST.SESSION.get('cps_display_params', {})
    sort_by = disp_params.get('sort_by', None);
    direction = disp_params.get('direction', 'asc');
elif not direction:
    direction = 'asc'

if sort_by == None:
    return context.filterContents(items=context.objectValues(),
                                  hide_folder=hide_folder,
                                  displayed=displayed)
else:
    return context.filterContents(items=context.objectValues(),
                                  sort_by=sort_by, direction=direction,
                                  hide_folder=hide_folder,
                                  displayed=displayed)
