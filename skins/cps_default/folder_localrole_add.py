##parameters=member_role, member_ids=[], search_param='', search_term='', REQUEST=None
# $Id$
"""Add new local roles

member_role is the role to be set, it will be added to users/groups ids listed
in member_ids, prefixed by 'user:' and 'group:'.

search_param and search_term parameters are only passed to be kept if addition
fails.
"""

from zLOG import LOG, DEBUG

from Products.CMFCore.utils import getToolByName
from urllib import urlencode

kwargs = {}

if not member_ids:
    kwargs['search_param']= search_param
    kwargs['search_term']= search_term
    kwargs['portal_status_message'] = 'psm_local_roles_select_members'
else:
    mtool = getToolByName(context, 'portal_membership')
    # separate users and groups
    user_ids = [user[len('user:'):] for user in member_ids
                if user.startswith('user:')]
    group_ids = [group[len('group:'):] for group in member_ids
                 if group.startswith('group:')]
    # set local roles
    mtool.setLocalRoles(context, user_ids,
                        member_role, reindex=0)
    mtool.setLocalGroupRoles(context, group_ids,
                             member_role, reindex=0)
    context.reindexObjectSecurity()
    kwargs['portal_status_message'] = 'psm_local_roles_changed'

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(
        '%s/folder_localrole_form?%s' %
        (context.absolute_url(), urlencode(kwargs)))

