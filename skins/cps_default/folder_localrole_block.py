##parameters=lr_block=None, lr_unblock=None, filtered_role=None, show_blocked_roles=0, REQUEST=None
# $Id$
"""
Block/unblock local roles acquisition

If lr_block is not None, block acquisition, else if lr_unblock is not None,
unblock acquisition.

Acquisition blocking is made adding/deleting the '-' role to the group of
anonymous users.

filtered_role and show_blocked_roles parameters are only passed to be kept
while blocking/unblocking.
"""

from zLOG import LOG, DEBUG
from urllib import urlencode
from Products.CMFCore.utils import getToolByName

pmtool = getToolByName(context, 'portal_membership')
member = pmtool.getAuthenticatedMember()
member_id = member.getUserName()

reindex = 0
kwargs = {}

if lr_block is not None:
    # For security, before blocking everything, we readd the current user
    # as a XyzManager of the current workspace/section.
    for r in context.getCPSCandidateLocalRoles():
        if r == 'Manager':
            continue
        if not r.endswith('Manager'):
            continue
        if not member.has_role(r, context):
            continue
        pmtool.setLocalRoles(context, (member_id,), r, reindex=0)
    # Block.
    pmtool.setLocalGroupRoles(context, ('role:Anonymous',), '-',
                              reindex=0)
    reindex = 1
    kwargs['portal_status_message'] = 'psm_local_roles_blocked'
elif lr_unblock is not None:
    pmtool.deleteLocalGroupRoles(context, ('role:Anonymous',), '-',
                                 reindex=0)
    reindex = 1
    kwargs['portal_status_message'] = 'psm_local_roles_unblocked'

if reindex == 1:
    context.reindexObjectSecurity()

if REQUEST is not None:
    kwargs['filtered_role'] = filtered_role
    kwargs['show_blocked_roles'] = show_blocked_roles
    REQUEST.RESPONSE.redirect('%s/folder_localrole_form?%s'%(
        context.absolute_url(), urlencode(kwargs)))

