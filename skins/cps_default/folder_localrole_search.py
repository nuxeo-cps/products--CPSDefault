##parameters=search_param=None, search_term=None
#$Id$

from AccessControl import Unauthorized

if not context.portal_membership.checkPermission('Change permissions', context):
    raise Unauthorized

if search_param in ('fullname', 'email'):
    mdir = context.portal_directories.members
    # first get portal member ids without externall call (e.g. LDAP)
    return_fields = ('id', 'givenName', 'sn', 'email')
    if search_param == 'fullname':
        # XXX cannot search both parameters at the same time because we want a
        # OR search, not AND.
        from_ids = mdir.searchEntries(id=search_term,
                                      return_fields=return_fields)
        from_fullnames = mdir.searchEntries(fullname=search_term,
                                            return_fields=return_fields)
        results = {}
        for id, values in (from_ids + from_fullnames):
            results[id] = values
        results = results.items()
        results.sort()
        return results
    elif search_param == 'email':
        return mdir.searchEntries(email=search_term,
                                     return_fields=return_fields)
elif search_param == 'groupname':
    gdir  = context.portal_directories.groups
    # XXX hardcoded but not GroupsDirectory's job
    pseudo_groups = ['role:Anonymous', 'role:Authenticated']
    groups = []
    for pseudo_group in pseudo_groups:
        if pseudo_group.lower().find(search_term) != -1:
            groups.append(pseudo_group)
    groups.extend(gdir.searchEntries(group=search_term))
    return groups
