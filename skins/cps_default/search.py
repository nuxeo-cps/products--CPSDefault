## Script (Python) "search"
##parameters=query={}, REQUEST=None, **kw
##title=Get content info used by macros
# $Id$
""" return a list of proxy matching the query
"""

if REQUEST is not None:
    kw.update(REQUEST.form)
kw.update(query)
query = kw

catalog = context.portal_catalog
ptool = context.portal_proxies
ttool = context.portal_types

# get searchable portal type only
okpt = context.getSearchablePortalTypes(only_ids=1)
pt = query.get('portal_type', None)
if pt and pt != ['']:
    pt = [t for t in pt if t in okpt]
else:
    pt = okpt
query['portal_type'] = pt

# query for document object
portal_path = context.portal_url.getPortalPath()
query['path'] = portal_path+'/portal_repository/'

review_state=''
if query.get('review_state'):
    review_state=query['review_state']
    wtool=context.portal_workflow
    del query['review_state']

items = []

results = catalog(**query)
for result in results:
    # XXX may be we should add Id as metadata
    id = result.getPath().split('/')[-1]
    infos = ptool.getProxiesFromObjectId(id)
    for info in infos:
        proxy = info['object']
        # prevent ZCatalog desynchronization
        try:
            title = proxy.Title()
        except (AttributeError):
            continue
        if not review_state or \
           wtool.getInfoFor(proxy,'review_state','nostate') == review_state:
            items.append(proxy)

return items
