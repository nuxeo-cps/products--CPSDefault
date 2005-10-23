##parameters=cps_roles, filtered_role=None
# $Id$
"""
XXX content moved into portal_membership
"""
from Products.CMFCore.utils import getToolByName
mtool = getToolByName(context, 'portal_membership')
return mtool.getCPSLocalRolesRender(context, cps_roles, filtered_role)

