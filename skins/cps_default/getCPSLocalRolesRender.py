##parameters=cps_roles, filtered_role=None, show_blocked_roles=0
# $Id$
"""
XXX content moved into portal_membership
"""
from Products.CMFCore.utils import getToolByName
mtool = getToolByName(context, 'portal_membership')
return mtool.getCPSLocalRolesRender(context, cps_roles, filtered_role,
                                    show_blocked_roles)
