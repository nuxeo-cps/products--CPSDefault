##parameters=allowed=1
# $Id$
"""Return content types information list, sorted by their localized title.

It keeps workspace/section types at the begining of the list,
if allowed is set return allowed content type for the context, else
return all searchable content type.
"""

if allowed:
    items = context.allowedContentTypes()
    allowed_by_wf = context.portal_workflow.getAllowedContentTypes(context)
    items = [x for x in items if x in allowed_by_wf]
else:
    items = context.getSearchablePortalTypes()

def l10n(s):
    cpsmcat = context.translation_service
    ret = cpsmcat(s)
    if same_type(ret, u''):
        # FIXME: unicodegeddon
        return ret.encode('iso-8859-15', 'ignore')
    else:
        return ret

def cmp_type(a, b):
    # Some types are favored so they show up at the top of the list
    if a.getId() in ('Workspace', 'Section'):
        return -1
    if b.getId() in ('Workspace', 'Section'):
        return 1
    aa = l10n(a.Title()).lower()
    bb = l10n(b.Title()).lower()
    return cmp(aa, bb)

items.sort(cmp_type)

return items
