##parameters=member_id
#$Id$
"""Return the member fullname given an id.

Lookup within all the members directories.
"""
mtool = context.portal_membership
return mtool.getFullnameFromId(member_id)
