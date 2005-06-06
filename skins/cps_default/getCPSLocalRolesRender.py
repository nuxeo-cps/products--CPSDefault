##parameters=cps_roles, filtered_role=None, show_blocked_roles=0
# $Id$
"""
Get dictionnaries that will be used by the template presenting local roles.

Return 2 lists and 2 dictionnaries: sorted members, members dictionnary
with member ids as keys and a dictionnary describing their roles as
values, and the same for groups.

Also return information about local roles blocking.

filtered_role and show_blocked_roles parameters are only passed to be kept or
changed while displaying roles.

Example:

sorted_members = ['user:test', 'user:toto', 'user:test4']

members = {
    'user:test': {
        'title': 'M. Test',
        'role_input_name': 'role_user_test',
        'has_local_roles': 1,
        'here_roles': {
            'WorkspaceManager': {'here': 1, 'inherited': 0},
            'WorkspaceReader': {'here': 0, 'inherited': 0},
            'WorkspaceMember': {'here': 0, 'inherited': 1},
            },
        'inherited_roles': {'WorkspaceMember': ['workspaces', 'workspaces/truc']},
        },
    'user:test4': {
        'title': 'Test3 euh 4',
        'role_input_name': 'role_user_test4',
        'has_local_roles': 0,
        'here_roles': {
            'WorkspaceManager': {'here': 0, 'inherited': 1},
            'WorkspaceReader': {'here': 0, 'inherited': 0},
            'WorkspaceMember': {'here': 0, 'inherited': 0},
            },
        'inherited_roles': {'WorkspaceManager': ['workspaces/truc']},
        },
    'user:toto': {
        'title': 'Romain Toto',
        'role_input_name': 'role_user_test5',
        'has_local_roles': 1,
        'here_roles': {
            'WorkspaceManager': {'here': 0, 'inherited': 0},
            'WorkspaceReader': {'here': 1, 'inherited': 1},
            'WorkspaceMember': {'here': 1, 'inherited': 0},
            },
        'inherited_roles': {'WorkspaceReader': ['workspaces']},
        },
    }

"""

from zLOG import LOG, DEBUG
from Products.CMFCore.utils import getToolByName

# directories, used for users/groups rendering
dirtool = getToolByName(context, 'portal_directories')
mdir = dirtool.members
mdir_title_field = mdir.title_field
gdir = dirtool.groups
gdir_title_field= gdir.title_field

#LOG("getCPSLocalRolesRender", DEBUG,
#    "filtered_role=%s, show_blocked_roles=%s"%(
#    filtered_role, show_blocked_roles))

mtool = getToolByName(context, 'portal_membership')
base_url = context.getBaseUrl()
context_url = context.getContextUrl()

dict_roles, local_roles_blocked = context.getCPSLocalRoles(cps_roles)

#LOG("getCPSLocalRolesRender", DEBUG,
#    "dict_roles=%s, local_roles_blocked=%s"%(dict_roles, local_roles_blocked))

# fill members and groups dictionnaries
members = {}
groups = {}
for item, role_infos in dict_roles.items():
    # fill info about each role for given item
    here_roles = {}
    inherited_roles = {}
    has_roles = 0
    has_local_roles = 0
    # default info for each role to be presented
    for role in cps_roles:
        here_roles[role] = {
            'here': 0,
            'inherited': 0,
            }
    for role_info in role_infos:
        role_url = role_info['url']
        if base_url + role_url == context_url:
            here = 1
        else:
            here = 0
        # maybe skip inherited blocked roles
        if here or not local_roles_blocked or show_blocked_roles:
            for role in role_info['roles']:
                # take filtering on roles into account
                if not filtered_role or role == filtered_role:
                    has_roles = 1
                # fill info even if role is filtered
                if here:
                    here_roles[role]['here'] = 1
                    has_local_roles = 1
                else:
                    here_roles[role]['inherited'] = 1
                    if inherited_roles.get(role) is None:
                        inherited_roles[role] = [role_url]
                    else:
                        inherited_roles[role].append(role_url)
    # skip if all roles have been filtered
    if not has_roles:
        continue
    # fill members and groups rendering info (title, input name) + computed
    # roles info
    if item.startswith('user:'):
        member_id = item[len('user:'):]
        member_title = ''
        entry = mdir.getEntry(member_id, None)
        if entry is not None:
            member_title = entry.get(mdir_title_field)
        members[item] = {
            'title': member_title or member_id,
            'role_input_name': 'role_user_' + member_id,
            'here_roles': here_roles,
            'inherited_roles': inherited_roles,
            'has_local_roles': has_local_roles,
            }
    elif item.startswith('group:'):
        group_id = item[len('group:'):]
        group_title = ''
        entry = gdir.getEntry(group_id, None)
        if entry is not None:
            group_title = entry.get(gdir_title_field)
        groups[item] = {
            'title': group_title or group_id,
            # XXX AT: no ':' accepted, change it for role:Anonymous and
            # role:Authenticated groups
            'role_input_name': 'role_group_' + group_id.replace(':', '_'),
            'here_roles': here_roles,
            'inherited_roles': inherited_roles,
            'has_local_roles': has_local_roles,
            }

# sort members and groups on title
sort = [(v.get(mdir_title_field), k) for k, v in members.items()]
sort.sort()
sorted_members = [x[1] for x in sort]
sort = [(v.get(gdir_title_field), k) for k, v in groups.items()]
sort.sort()
sorted_groups = [x[1] for x in sort]

#LOG("getCPSLocalRolesRender", DEBUG,
#    "sorted_members=%s, members=%s"%(sorted_members, members))
#LOG("getCPSLocalRolesRender", DEBUG,
#    "sorted_groups=%s, groups=%s"%(sorted_groups, groups))

return sorted_members, members, sorted_groups, groups, local_roles_blocked
