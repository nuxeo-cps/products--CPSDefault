## Script (Python) "getFolderContents"
##parameters=sort_by='title', direction='asc', hide_folder=0
# $Id$
"""
Get a sorted list of contents object
"""

cps_cookie = context.REQUEST.SESSION.get('cps_preferences', {}) 
sort_by    = cps_cookie.get('cps_display_order', 'titre');
direction  = cps_cookie.get('cps_display_direction', 'asc');

return context.filterContents(items=context.objectValues(),
                              sort_by=sort_by, direction=direction,
                              hide_folder=hide_folder)
