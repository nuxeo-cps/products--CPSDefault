## Script (Python) "getFolderContents"
##parameters=sort_by='date', direction='asc'
# $Id$
"""
Get a sorted list of contents object
"""
return context.filterContents(items=context.objectValues(),
                              sort_by=sort_by, direction=direction)
