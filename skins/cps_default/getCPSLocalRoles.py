##parameters=cps_roles
# $Id$
"""
Get local roles dictionnary filtered using relevant roles in context and
tell if local roles are blocked using this dictionnary

Example of dictionnary returned:
dict_roles = {
    'user:test': [
        {'url': 'workspaces/members',
         'roles': ['WorkspaceReader', 'WorkspaceMember']},
        {'url': 'workspaces',
         'roles': ['WorkspaceReader']},
        ],
    'group:machin': [
        {'url': 'workspaces/truc',
         'roles': ['WorkspaceManager']},
        ],
    'group:role:Anonymous': [
        {'url': 'workspaces/members',
         'roles': ['WorkspaceMember', 'WorkspaceReader']},
        {'url': 'workspaces',
         'roles': ['WorkspaceReader']},
        ],
    }
"""

from zLOG import LOG, DEBUG
from Products.CMFCore.utils import getToolByName

# Get local roles settings from the membership tool
mtool = getToolByName(context, 'portal_membership')
dict_roles = mtool.getMergedLocalRolesWithPath(context)
local_roles_blocked = 0

# Filter special roles, and only take local roles
for item, role_infos in dict_roles.items():
    for role_info in role_infos:
        roles = role_info['roles']
        if item == "group:role:Anonymous" and "-" in roles:
            local_roles_blocked = 1
        # filter with roles in context
        role_info['roles'] = [r for r in roles if r in cps_roles]
    dict_roles[item] = [x for x in dict_roles[item] if x['roles']]
    # delete items that do not have any role to display
    if not dict_roles[item]:
        del dict_roles[item]

#LOG("getCPSLocalRoles", DEBUG, "cps_roles=%s, dict_roles=%s, "
#    "local_roles_blocked=%s" %(cps_roles, dict_roles, local_roles_blocked))

return dict_roles, local_roles_blocked
