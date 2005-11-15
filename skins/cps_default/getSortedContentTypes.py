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

cpsmcat = context.translation_service

def l10n(msgid):
    """return l10n msgid or msgid."""
    ret = cpsmcat(msgid)
    if same_type(ret, u''):
        # FIXME: unicodegeddon
        ret = ret.encode('iso-8859-15', 'ignore')
    elif ret is None:
        ret = msgid
    return ret

def make_sort_key(ctype, title):
    """Create a sort key for a content type.

    Keeping workspace/section types at the begining of the list."""
    if ctype == 'Section':
        return 1
    elif ctype == 'Workspace':
        return 2
    return l10n(title).lower()

items = [(make_sort_key(x.getId(), x.Title()), x) for x in items]
items.sort()
items = [x[1] for x in items]

return items
