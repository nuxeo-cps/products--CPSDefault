##parameters=
##parameters=search_param=None, search_term=None
#$Id$

#
# Test to stay up :)
#
portal = context.portal_url.getPortalObject()
portal_objects = portal.objectIds()

if 'portal_metadirectories' not in portal_objects:
    return []
else:
    dtool   = context.portal_metadirectories

dtool_dirs = dtool.objectIds()

if search_param in ['email', 'fullname'] \
   and 'members' not in dtool_dirs:
    return []
else:
    members = dtool.members

if search_param == 'groupname' \
   and 'groups' not in dtool_dirs:
    return []
else:
    groups  = dtool.groups

#
# Here we go for the research !
#
if search_param == 'fullname':
    return members.searchEntry(**{'id_':search_term, 'fullname':search_term})
elif search_param == 'email':
    return members.searchEntry(**{'email':search_term})
elif search_param == 'groupname':
    return groups.searchEntry(**{'id_':search_term, 'title_':search_term})
else:
    return []
