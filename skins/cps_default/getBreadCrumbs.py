## Script (Python) "getBreadCrumbs.py"
##parameters=url=None, parent=0, breadcrumb_set=None
# $Id$

def format_title(title):
    l = len(title)
    ml = 20
    if l > ml:
        short_title = title[:ml-6]+ '...' + title[l-3:]
    else:
        short_title = title
    return short_title

#
# Faking the real path by setting
# a variable "breadcrumb_set" in the REQUEST
# and then returning it without computing
# Cf. Directories Templates
#if REQUEST is not None:
#    if REQUEST.has_key('breadcrumb_set'):
#        return getattr(REQUEST, 'breadcrumb_set', None)

if breadcrumb_set != None:
    return breadcrumb_set

if not url:
    url = context.getPortalUrl()
path = url.split('/')
path = filter(None, path)
if parent:
    path = path[:-1]

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
