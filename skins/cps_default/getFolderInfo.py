## Script (Python) "getFolderInfo"
##parameters=
# $Id$
""" Called by portal_tree for additional information on folder  """

title_or_id = context.title_or_id()
short_title = (len(title_or_id) > 15) and title_or_id[:15] + '...' or title_or_id

return {'title': context.Title(),
        'title_or_id': title_or_id,
        'short_title': short_title,
        }
