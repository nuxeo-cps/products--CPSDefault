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
if context.portal_type == 'Section':
    manager_role = 'SectionManager'
elif context.portal_type == 'Workspace':
    manager_role = 'WorkspaceManager'
else:
    manager_role = None

merged_roles = context.portal_membership.getMergedLocalRoles(context)

managers = []

if manager_role:
    for user,roles in merged_roles.items():
        if user.startswith('user:') and manager_role in roles:
            managers.append(user[5:])

return {'title': context.Title(),
        'title_or_id': title_or_id,
        'short_title': short_title.replace(' ', '&nbsp;'),
        'description': description,
        'managers': managers,
        }
