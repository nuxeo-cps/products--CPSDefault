##parameters=url=None, parent=0, breadcrumb_set=None
# $Id$
"""
FIXME: add docstring.
"""

ml = 20

def format_title(title):
    l = len(title)
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
#

if breadcrumb_set != None:
    return breadcrumb_set

if url is None:
    url = context.getBaseUrl()

path = url.split('/')
path = filter(None, path)
if parent:
    path = path[:-1]

portal = context.portal_url.getPortalObject()
portal_id = portal.getId()
checkPermission = context.portal_membership.checkPermission
items = []

for i in range(len(path)):
    ipath = path[:i+1]
    obj = portal.restrictedTraverse(ipath)
    if not checkPermission('View', obj):
        continue
    title = obj.title_or_id()
    try:
        is_archived = obj.isProxyArchived()
    except AttributeError:
        is_archived = 0
    if is_archived:
        # XXX i18n
        title = 'v%s (%s)' % (obj.getRevision(), title)
    rpath = '/'.join(ipath)
    url = '/%s/' % rpath
    # all containers but portal should be accessed by their 'view' action
    if ipath[-1] != portal_id:
        url = url + 'view'
    items.append({'id': ipath[-1],
                  'title': format_title(title),
                  'longtitle': title,
                  'url': url,
                  'rpath': rpath,
                 })

return items
