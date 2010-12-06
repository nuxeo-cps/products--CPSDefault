##parameters=allowed=1,custom_order=False
# $Id$
"""Return content types information list, sorted by their localized title.

It keeps workspace/section types at the begining of the list,
if allowed is set return allowed content type for the context, else
return all searchable content type.
"""
if allowed:
    allowed_by_wf = context.portal_workflow.getAllowedContentTypes(context)
    allowed_by_wf = [x.getId() for x in allowed_by_wf]
    items = context.allowedContentTypes()
    items = [x for x in items if x.getId() in allowed_by_wf]
else:
    items = context.getSearchablePortalTypes()

cpsmcat = context.translation_service

infos = []
for item in items:
    info = dict(id=item.getId(), icon=item.getIcon())
    title = item.Title()
    descr = item.Description()
    try:
        i18n = item.is_i18n
    except AttributeError:
        # Only CPS Flexible Type Information portal_types have
        # the is_i18n attribute which is not the case for at least the Wiki
        # and Wiki Page which are Factory-based Type Information portal_types.
        i18n = True
    if i18n:
        title = cpsmcat(title)
        descr = cpsmcat(descr)
    info['Title'] = title
    info['Description'] = descr
    infos.append(info)

def make_sort_key(info, custom_order):
    """Create a sort key for a content type.

    Keeping workspace/section types at the begining of the list.
    If custom_order is True, move the specific types to
    the top of the list, just behind workspace/section"""
    ctype = info['id']
    if ctype == 'Section':
        return 1
    elif ctype == 'Workspace':
        return 2
    if custom_order is True:
        if ctype == 'News Item':
            return 3
        elif ctype == 'Document':
            return 4
        elif ctype == 'File':
            return 5
        elif ctype == 'Link':
            return 6
    return info['Title'].lower()

infos = [(make_sort_key(i, custom_order), i) for i in infos]
infos.sort()
return [x[1] for x in infos]
