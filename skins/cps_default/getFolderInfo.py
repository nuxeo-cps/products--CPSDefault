## Script (Python) "getFolderInfo"
##parameters=
# $Id$
""" Called by portal_tree for additional information on folder  """

from zLOG import LOG, DEBUG

title_or_id = context.title_or_id()
l = len(title_or_id)
ml = 25
if l > ml:
    short_title = title_or_id[:ml-6]+ '...' + title_or_id[l-3:]
else:
    short_title = title_or_id

try:
    doc = context.getContent()
except AttributeError:
    # not a proxy
    doc = context
description = doc.Description() or ''

#get all managers of this folder
#XXX: do something cleaner than that for dececting whether
#we are in a section or a workspace
if context.absolute_url().find('sections') != -1:
    manager_role = 'SectionManager'
else:
    manager_role = 'WorkspaceManager'

roles = context.portal_membership.getMergedLocalRoles(context)

dtool = context.portal_metadirectories.members

managers = []

for pair in roles.items():
    if pair[0].startswith('user:') and manager_role in pair[1]:
        manager = pair[0][5:]
        if dtool.getEntry(manager):
            managers.append(manager)

return {'title': context.Title(),
        'title_or_id': title_or_id,
        'short_title': short_title.replace(' ', '&nbsp;'),
        'description': description,
        'managers': managers,
        }
