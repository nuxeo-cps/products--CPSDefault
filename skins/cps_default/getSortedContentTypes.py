##parameters=
# $Id$
""" Sorting for display PortalFolder.py: allowedContentTypes """
items = context.allowedContentTypes()

def cmp_type(a, b):
    # we like workspaces and section
    if a.getId() in ('Workspace', 'Section'):
        return -1
    if b.getId() in ('Workspace', 'Section'):
        return 1
    aa = a.Title()
    bb = b.Title()
    if len(a.allowed_content_types):
        aa = '0' + aa
    else:
        aa = '1' + aa
    if len(b.allowed_content_types):
        bb = '0' + bb
    else:
        bb = '1' + bb
    return cmp(a.Title(), b.Title())

items.sort(cmp_type)
allowed = context.portal_types[context.getPortalTypeName()].allowed_content_types
items = [i for i in items if i.getId() in allowed]

return items
