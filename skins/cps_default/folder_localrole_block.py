##parameters=lr_block=None, lr_unblock=None, filtered_role=None, show_blocked_roles=0, REQUEST=None
# $Id$
"""
XXX content moved into portal_membership
"""
from Products.CMFCore.utils import getToolByName
mtool = getToolByName(context, 'portal_membership')

mtool.folderLocalRoleBlock(context, lr_block, lr_unblock,
                           filtered_role, show_blocked_roles, REQUEST)
