## Script (Python) "getBreadCrumbs.py"
##parameters=url=None
# $Id$

def format_title(title):
    l = len(title)
    ml = 20
    if l > ml:
        short_title = title[:ml-6]+ '...' + title[l-3:]
    else:
        short_title = title
    return short_title

if not url:
    url = context.getPortalUrl()
path = url.split('/')
path = filter(None, path)

portal = context.portal_url.getPortalObject()
mtool = context.portal_membership
items = []
for i in range(len(path)):
    ipath = path[:i+1]
    obj = portal.restrictedTraverse(ipath)
    if not mtool.checkPermission('View', obj):
        continue
    title = obj.Title() or obj.getId()
    items.append({'id': ipath[-1],
                   'title': format_title(title),
                   'longtitle': title,
                   'url': '/' + '/'.join(ipath),
                   })

return items
