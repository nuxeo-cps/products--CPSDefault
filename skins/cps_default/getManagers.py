## Script (Python) "getWorkspaceManagers"
##parameters=rpath
# $Id$
"""get all managers declared for workspace/section whose rpath is rpath"""

from zLOG import LOG,DEBUG

if rpath.startswith('sections'):
    manager_role = 'SectionManager'
else:
    manager_role = 'WorkspaceManager'

portal = context.portal_url.getPortalObject()

roles = context.portal_membership.getMergedLocalRoles(
                                         portal.restrictedTraverse(rpath))

dtool = context.portal_metadirectories.members
portal_url = context.portal_url.getPortalPath()
dtool_entry_url = "%s/directory_getentry?dirname=%s&entry_id=" \
                  % (portal_url, dtool.id)

result = []

for pair in roles.items():
    if pair[0].startswith('user:') and manager_role in pair[1]:
        manager = pair[0][5:]
        entry = dtool.getEntry(manager)
        if entry:
            result.append((entry.get('fullname',manager),
                           dtool_entry_url + manager))

return result
