## Script (Python) "getBreadCrumbs.py"
##parameters=include_root=1
##title=Return breadcrumbs
##
from string import join

result = []
portal_url = context.portal_url(relative=1) + '/'

if include_root:
    title = context.portal_properties.title().strip()
    result.append( { 'id': 'root'
                   , 'title': (len(title) > 15) and title[:15] + '...' or title
                   , 'longtitle': title
                   , 'url': portal_url
                   }
                 )

relative = context.portal_url.getRelativeContentPath(context)
portal = context.portal_url.getPortalObject()

for i in range(len(relative)):
    now = relative[:i+1]
    obj = portal.restrictedTraverse(now)
    if not now[-1] == 'talkback':
        title = obj.Title() or obj.getId().strip()
        result.append( { 'id': now[-1]
                       , 'title': (len(title) > 12) and title[:12] + '...' or title
                       , 'longtitle': title
                       , 'url': portal_url + join(now, '/') + '/'
                       }
                    )

return result
