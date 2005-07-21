##parameters=url=None, parent=0, breadcrumb_set=None
# $Id$
"""
DO NOT USE THIS DEPRECATED SCRIPT, QUERY URL TOOL INSTEAD: this script may
break with some virtual hosting configurations.
If breadcrumb_set is not None, then no need to query the url tool.
Exemple of query:
context.portal_url.getBreadCrumbsInfo(context, parent, title_size)


Return breadcrumbs for the given context

url is the url of the object we want breadcrumbs for.
if parent is set to 1, the object itself is not in the breadcrumbs list.

if breadcrumbs_set is not None, the real path is faked by setting a variable
'breadcrumb_set' in the REQUEST and then returning it without computing
(Cf. Directories Templates)
"""

from zLOG import LOG, DEBUG
from Products.CMFCore.utils import getToolByName

ml = 20

breadcrumbs = []
if breadcrumb_set is not None:
    breadcrumbs = breadcrumb_set
else:
    utool = getToolByName(context, 'portal_url')
    if url is None:
        content = utool.getPortalObject()
    else:
        # XXX may break in virtual hosting environment
        content = utool.restrictedTraverse(url, None)
        if content is None:
            content = context

    breadcrumbs = utool.getBreadCrumbsInfo(context=content,
                                           only_parents=parent)

return breadcrumbs
