##parameters=
# $Id$
"""
XXX content moved into portal_membership

Override this template if you have new portal types or new roles with a
specific mapping to register.
"""
from Products.CMFCore.utils import getToolByName
mtool = getToolByName(context, 'portal_membership')
return mtool.getCPSCandidateLocalRoles(context)
