##parameters=cps_roles=None
# $Id$
"""
XXX content moved into portal_membership
"""
from Products.CMFCore.utils import getToolByName
mtool = getToolByName(context, 'portal_membership')
return mtool.getCPSLocalRoles(context, cps_roles)