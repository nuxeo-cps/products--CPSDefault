## Script (Python) "getFolderInfo"
##parameters=
# $Id$
""" Called by portal_tree for additional information on folder  """

title_or_id = context.title_or_id()
l = len(title_or_id)
ml = 25
if l > ml:
    short_title = title_or_id[:ml-6]+ '...' + title_or_id[l-3:]
else:
    short_title = title_or_id

return {'title': context.Title(),
        'title_or_id': title_or_id,
        'short_title': short_title.replace(' ', '&nbsp;'),
        }
