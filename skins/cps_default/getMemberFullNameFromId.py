##parameters=member_id
#$Id$
"""Return the member fullname given an id.

Lookup within all the members directories.
"""

pdirectories=context.portal_directories
directories=[pdirectories.members]

for directory in directories:
    try:
        member = directory.getEntry(member_id)
        return member.get('fullname', member_id)
    except (KeyError, ValueError):
        pass
return member_id
