##parameters=doc=None
# $Id$
""" Called by portal_tree for additional information on folder  """

# Warning when submiting a folderish document you don't have the
# View permission on the new proxy because it is in a pending state
# this is why you should not use proxy.xxx methods
proxy = context
if doc is None:
    doc = proxy.getContent()

title_or_id = proxy.title_or_id()
l = len(title_or_id)
ml = 25
mml = (ml-3)/2
if l > ml:
    short_title = title_or_id[:mml]+ '...' + title_or_id[-mml:]
else:
    short_title = title_or_id

description = doc.Description() or ''
hidden_folder = 0
if hasattr(doc.aq_explicit, 'hidden_folder'):
    hidden_folder = doc.hidden_folder
#get all managers of this folder
if doc.portal_type == 'Section':
    manager_role = 'SectionManager'
elif doc.portal_type == 'Workspace':
    manager_role = 'WorkspaceManager'
else:
    manager_role = None

merged_roles = doc.portal_membership.getMergedLocalRoles(proxy)

managers = []

if manager_role:
    for user,roles in merged_roles.items():
        if user.startswith('user:') and manager_role in roles:
            managers.append(user[5:])

return {'title': doc.Title(),
        'title_or_id': title_or_id,
        'short_title': short_title.replace(' ', '&nbsp;'),
        'description': description,
        'managers': managers,
        'hidden_folder': hidden_folder,
        }
