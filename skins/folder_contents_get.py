##parameters=get_pubsections=0
"""
Get a datastructure describing what's in a folder.
"""
isinworkspace = (context.portal_type == 'Workspace') # XXX hardcoded

docinfos = []
for item in context.objectValues():
    if item.getId().startswith('.'):
        continue
    d = context.content_info_get(item=item)
    if get_pubsections:
        # find info about publication
        # XXX check that we're dealing with a proxy here...
        pubsections = {
            'pending': [],
            'published': [],
            }
        for pubinfo in item.proxy_info_get(get_history=0)['pubinfos']:
            review_state = pubinfo['review_state']
            pubsections.setdefault(review_state, []).append(pubinfo)
        d['pubsections'] = pubsections
    docinfos.append(d)

# Sort

def thecmp(a, b):
    return (-cmp(a['folderish'], b['folderish']) or        # folders
            cmp(a['title'].lower(), b['title'].lower()) or # then by title
            0
            )

#docinfos.sort(thecmp)

return docinfos
