##parameters=allowed=1
# $Id$
""" Sorting for display allowedContentTypes
    if allowed=0 return Searchable portaltype"""

if allowed:
    items = context.allowedContentTypes()
else:
    items = context.getSearchablePortalTypes()

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

if allowed:
    ti = getattr(context.portal_types, context.getPortalTypeName(), None)
    if ti is not None:
        items = [i for i in items if i.getId() in ti.allowed_content_types]
    else:
        items = []

items.sort(cmp_type)

return items
