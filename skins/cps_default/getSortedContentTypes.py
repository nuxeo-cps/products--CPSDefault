##parameters=
# $Id$
""" Sorting for display PortalFolder.py: allowedContentTypes """
items = context.allowedContentTypes()

def l10n(s):
    cpsmcat = context.Localizer.default
    ret = cpsmcat(s)
    if same_type(ret, u''):
        return ret.encode('iso-8859-15', 'ignore')
    else:
        return ret

def cmp_type(a, b):
    # we like workspaces and section
    if a.getId() in ('Workspace', 'Section'):
        return -1
    if b.getId() in ('Workspace', 'Section'):
        return 1
    aa = l10n(a.Title()).lower()
    bb = l10n(b.Title()).lower()
    return cmp(aa, bb)

items.sort(cmp_type)
allowed = context.portal_types[context.getPortalTypeName()].allowed_content_types
items = [i for i in items if i.getId() in allowed]
items.sort(cmp_type)

return items
