## Script (Python) "getFolderContents"
##parameters=sort_by='title', direction='asc', hide_folder=0
# $Id$
"""
Get a sorted list of contents object
"""
return context.filterContents(items=context.objectValues(),
                              sort_by=sort_by, direction=direction,
                              hide_folder=hide_folder)
