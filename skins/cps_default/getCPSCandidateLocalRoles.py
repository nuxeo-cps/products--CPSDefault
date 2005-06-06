##parameters=
# $Id$
"""
Get relevant local roles according to the context.

Roles are already filtered using the membership tool getCPSCandidateLocalRoles
method, now filter them according to the context.

XXX: this should be handled by the membership tool, and should not be so
tricky.
"""

from zLOG import LOG, DEBUG
from Products.CMFCore.utils import getToolByName

# List local roles according to the context
mtool = getToolByName(context, 'portal_membership')
cps_roles = mtool.getCPSCandidateLocalRoles(context)
cps_roles.reverse()

# XXX a better way of doing is that is necessarly

# Filter them for CPS
cps_roles = [x for x in cps_roles if x not in ('Owner',
                                               'Member',
                                               'Reviewer',
                                               'Manager',
                                               'Authenticated')]
# filter roles by portal type using prefix
# XXX TODO relevant roles should be store in the portal_types tool
ptype_role_prefix = {'Section': ('Section',),
                     'Workspace': ('Workspace'),
                     'Wiki': ('Contributor', 'Reader'),
                     'Calendar': ('Workspace',),
                     'CPSForum': ('Forum',),
                     'Chat': ('Chat',),
                     }
ptype = context.portal_type
if ptype in ptype_role_prefix.keys():
    contextual_roles = []
    for role_prefix in ptype_role_prefix[ptype]:
        for cps_role in cps_roles:
            if cps_role.startswith(role_prefix):
                contextual_roles.append(cps_role)
    cps_roles = contextual_roles

#LOG("getCPSCandidateLocalRoles", DEBUG, "cps_roles=%s"%(cps_roles,))

return cps_roles
