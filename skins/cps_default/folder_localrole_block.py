##parameters=lr_block=None, lr_unblock=None, filtered_role=None, show_blocked_roles=0, REQUEST=None
# $Id$
"""
Block/unblock local roles

If lr_block is not None, block local roles, elif lr_unblock is not None,
unblock them.
filtered_role and show_blocked_roles parameters are only passed to be kept
while blocking/unblocking.
"""

from Products.CMFCore.utils import getToolByName
from urllib import urlencode

mtool = getToolByName(context, 'portal_membership')
psm = ''
if lr_block is not None:
    mtool.blockLocalRoles(context)
    psm = 'psm_local_roles_blocked'
elif lr_unblock is not None:
    mtool.unblockLocalRoles(context)
    psm = 'psm_local_roles_unblocked'

if REQUEST is not None:
    kwargs = {
        'filtered_role': filtered_role,
        'show_blocked_roles': show_blocked_roles,
        'portal_status_message': psm,
        }
    REQUEST.RESPONSE.redirect('%s/folder_localrole_form?%s'%(
        context.absolute_url(), urlencode(kwargs)))
