## Script (Python) "getFolderContents"
##parameters=sort_by=None, direction=None, hide_folder=0
# $Id$
"""
Get a sorted list of contents object
"""
if not sort_by:
    cps_cookie = context.REQUEST.SESSION.get('cps_preferences', {})
    sort_by    = cps_cookie.get('cps_display_order', 'title');
    direction  = cps_cookie.get('cps_display_direction', 'asc');
elif not direction:
    direction = 'asc'

return context.filterContents(items=context.objectValues(),
                              sort_by=sort_by, direction=direction,
                              hide_folder=hide_folder)
