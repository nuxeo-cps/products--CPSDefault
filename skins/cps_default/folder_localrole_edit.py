##parameters=delete_ids=[], edit_ids=[], filtered_role=None, REQUEST=None, **kw
# $Id$
"""Edit local roles (delete/edit)

Edition is done if request or additional kws have the 'edit_local_roles' key,
otherwise deletion is done.

delete_ids are the ids of users/groups that have to be deleted, prefixed by
'user:' and 'group:'.

edit_ids are the ids of users/groups that will be edited (e.g, all users and
groups displayed on the page), prefixed by 'user:' and 'group:'.
Local roles to be set for each of these ids are given in the additional
keywords or in the request form. For instance, if user 'toto' has to have roles
'WorkspaceManager' and 'WorkspaceReader', kw or request will hold a key
'role_user_toto' with associated value ['WorkspaceManager',
'WorkspaceReader']. The group 'tata' will have the associated key
'role_group_tata'.

filtered_role parameter is only passed to be kept while editing.
"""

# XXX AT: if user changes its own rights and loses the "change permissions",
# all the roles will not be set correctly (they will be set until he/she loses
# its rights in the algorythm)

from zLOG import LOG, DEBUG
from urllib import urlencode
from Products.CMFCore.utils import getToolByName

kwargs = {}
reindex = False

if REQUEST is not None:
    kw.update(REQUEST.form)

# decide whether we'are adding or deleting roles.
edit = kw.has_key('edit_local_roles')

mtool = getToolByName(context, 'portal_membership')

if edit:
    # Edit: consider edit_ids and other edit settings that will have to be
    # 'guessed'
    if not edit_ids:
        kwargs['portal_status_message'] = 'psm_local_roles_no_editable_ids'
    else:
        user_ids = [user[len('user:'):] for user in edit_ids
                    if user.startswith('user:')]
        group_ids = [group[len('group:'):] for group in edit_ids
                     if group.startswith('group:')]
        cps_roles = context.getCPSCandidateLocalRoles()
        # users
        for user_id in user_ids:
            # get associated roles to set
            role_input_name = 'role_user_' + user_id
            roles = kw.get(role_input_name)
            if roles is None:
                # no roles anymore, delete it
                for role in cps_roles:
                    mtool.deleteLocalRoles(context, [user_id],
                                           reindex=0, recursive=0,
                                           member_role=role)
                if cps_roles:
                    reindex = True
            else:
                # only set roles accepted in context
                roles = [x for x in roles if x in cps_roles]
                roles_to_del = [x for x in cps_roles if x not in roles]
                for role in roles:
                    mtool.setLocalRoles(context, [user_id],
                                        role, reindex=0)
                for role in roles_to_del:
                    mtool.deleteLocalRoles(context, [user_id],
                                           reindex=0, recursive=0,
                                           member_role=role)
                if roles or roles_to_del:
                    reindex = True
        # groups
        for group_id in group_ids:
            # get associated roles to set
            # XXX AT: no ':' accepted, change it for role:Anonymous and
            # role:Authenticated groups
            role_input_name = 'role_group_' + group_id.replace(':', '_')
            roles = kw.get(role_input_name, [])
            # only set roles accepted in context
            roles = [x for x in roles if x in cps_roles]
            roles_to_del = [x for x in cps_roles if x not in roles]
            for role in roles:
                mtool.setLocalGroupRoles(context, [group_id],
                                         role, reindex=0)
            for role in roles_to_del:
                mtool.deleteLocalGroupRoles(context, [group_id],
                                            role=role, reindex=0)
            if not reindex and (roles or roles_to_del):
                reindex = True
        kwargs['portal_status_message'] = 'psm_local_roles_changed'
else:
    # Delete: consider delete_ids
    if not delete_ids:
        kwargs['portal_status_message'] = 'psm_local_roles_select_members'
    else:
        user_ids = [user[len('user:'):] for user in delete_ids
                    if user.startswith('user:')]
        group_ids = [group[len('group:'):] for group in delete_ids
                     if group.startswith('group:')]
        cps_roles = context.getCPSCandidateLocalRoles()
        for role in cps_roles:
            mtool.deleteLocalRoles(context, user_ids,
                                   reindex=0, recursive=0,
                                   member_role=role)
            mtool.deleteLocalGroupRoles(context, group_ids,
                                        role=role, reindex=0)
        if cps_roles:
            reindex = True
        kwargs['portal_status_message'] = 'psm_local_roles_changed'

if reindex:
    context.reindexObjectSecurity()

if REQUEST is not None:
    kwargs['filtered_role'] = filtered_role
    REQUEST.RESPONSE.redirect('%s/folder_localrole_form?%s'%(
        context.absolute_url(), urlencode(kwargs)))
