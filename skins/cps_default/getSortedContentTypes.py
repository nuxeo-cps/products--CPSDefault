##parameters=
# $Id$
""" Sorting for display PortalFolder.py: allowedContentTypes """
items = context.allowedContentTypes()

def cmp_type(a, b):
    if a.getId() in ('Workspace', 'Section'):
        return -1
    if b.getId() in ('Workspace', 'Section'):
        return 1
    # we like workspaces and section
    cpsmcat = context.Localizer.default
    aa = cpsmcat(a.Title())
    bb = cpsmcat(b.Title())
    return cmp(aa, bb)

items.sort(cmp_type)
allowed = context.portal_types[context.getPortalTypeName()].allowed_content_types
items = [i for i in items if i.getId() in allowed]

return items
