##parameters=mtool=None, base_url=None, context_url=None
# $Id$
"""
Get Merged Local Roles filtering non CPS roles.

Returns a complicated structure in the form of a tuple that contains:
  * A very complicated dictionary of role definitions
  * A list of editable users (XXX: What is it?)
  * The CPS roles available in this context
  * If there the local roles acquisition is blocked in this context
  * A dictionary of usernames and user real life names

Example
-------
proxy = self.restrictedTraverse(rpath)
local_roles = proxy.getCPSLocalRoles()
local_roles
(
 {'user:a1': [{'url': 'workspaces', 'roles': ['WorkspaceMember']}],
  'group:role:Anonymous': [{'url': 'workspaces', 'roles': ['WorkspaceReader']}]
  },
 ['user:a1', 'group:role:Anonymous'],
 ['WorkspaceReader', 'WorkspaceMember', 'WorkspaceManager'],
 0,
 {'a1': 'Joe User'}
)
"""

if mtool is None:
    mtool = context.portal_membership

if base_url is None:
    base_url = context.getBaseUrl()

if context_url is None:
    context_url = context.getContextUrl()

# Get the list of Roles from the tool
dict_roles = mtool.getMergedLocalRolesWithPath(context)

# Filter remove special roles
local_roles_blocked = 0
for user in dict_roles.keys():
    for item in dict_roles[user]:
        roles = item['roles']
        roles = [r for r in roles if r not in ('Owner', 'Member')]
        if user == 'group:role:Anonymous' and '-' in roles:
            roles = [r for r in roles if r != '-']
            if base_url+item['url'] == context_url:
                local_roles_blocked = 1
        item['roles'] = roles

    dict_roles[user] = [x for x in dict_roles[user] if x['roles']]

    if not dict_roles[user]:
        del dict_roles[user]

#find editable user with local roles defined in the context
editable_users = []
for user in dict_roles.keys():
    for item in dict_roles[user]:
        if base_url+item['url'] == context_url:
            editable_users.append(user)
            continue

# List local roles according to the context
cps_roles = mtool.getCPSCandidateLocalRoles( context )
cps_roles.reverse()

# XXX a better way of doing is that is necessarly

# Filter them for CPS
cps_roles = [x for x in cps_roles if x not in ('Owner',
                                               'Member',
                                               'Reviewer',
                                               'Manager',
                                               'Authenticated')]
# filter roles by portal type using prefix
# XXX TODO relevant roles should be store in the portal_types tool
ptype_role_prefix = {'Section': 'Section',
                     'Workspace': 'Workspace',
                     'Calendar': 'Workspace',
                     'CPSForum': 'Forum',
                     'CPSChat': 'Chat',
                     }
ptype = context.portal_type
if ptype in ptype_role_prefix.keys():
    prefix = ptype_role_prefix[ptype]
    cps_roles = [x for x in cps_roles if x.startswith(prefix)]

# user_names is a dictionary that holds the fullnames of users in
# dict_roles.keys()
mdir = context.portal_directories.members
user_names = {}
for user in dict_roles.keys():
    type, uid = user.split(':', 1)
    if type=='user':
        user_names[uid] = mdir.getEntry(uid, {}).get('fullname', uid)

return dict_roles, editable_users, cps_roles, local_roles_blocked, user_names
