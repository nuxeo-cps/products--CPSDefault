##parameters=REQUEST=None, query={}, sort_by=None, direction=None, hide_folder=0, folder_prefix=None, start_date=None, end_date=None, allow_empty_search=0
# $Id$
""" return a list of proxy matching the query """

from zLOG import LOG, DEBUG

if REQUEST is not None:
    query.update(REQUEST.form)

# check for empty search:
if not allow_empty_search:
    qv = filter(None, query.values())
    if not qv or (len(qv) == 2 and
                  str(query.get('modified')) == '1970/01/01'):
        return []

catalog = context.portal_catalog
ptool = context.portal_proxies

# get searchable portal type only
okpt = context.getSearchablePortalTypes(only_ids=1)
pt = query.get('portal_type', None)
if pt is not None:
    # The query can contain a single portal_type or a list of portal_types
    if same_type(pt, ''):
        pt = [pt]

del_portal_type = 0
if pt and pt != ['']:
    pt = [t for t in pt if t in okpt]
else:
    del_portal_type = 1
    pt = okpt
query['portal_type'] = pt

# search the document repository
portal_path = context.portal_url.getPortalPath()
query['path'] = portal_path+'/portal_repository/'

# init status
status=''
if query.get('review_state'):
    status = query['review_state']
    wtool = context.portal_workflow
    del query['review_state']

# search and get documents brains
# XXX : When this script is called from the unit tests environment no document
# brains are ever returned by the catalog. Why ?
b_docs = catalog(**query)

# restore query as it is pass trought request.form
del query['path']
if del_portal_type:
    del query['portal_type']
if status:
    query['review_state'] = status


items = []
for b_doc in b_docs:
    doc_id = b_doc.getPath().split('/')[-1]
    # get all visible proxies information with the same doc_id
    i_proxies = ptool.getProxiesFromObjectId(doc_id,
                                             proxy_rpath_prefix=folder_prefix)
    for i_proxy in i_proxies:
        proxy = i_proxy['object']

        # prevent zcatalog desynchronization ??
        try:
            title = proxy.Title()
        except (AttributeError):
            continue

        # status filtering
        if (status and
            wtool.getInfoFor(proxy, 'review_state','nostate') != status):
            continue

        # event start/end filtering
        if start_date and end_date:
            doc = proxy.getContent()
            sd = ed = 0
            if hasattr(doc.aq_explicit, 'start'):
                if callable(doc.start):
                    sd = doc.start()
                else:
                    sd = doc.start
            if hasattr(doc.aq_explicit, 'end'):
                if callable(doc.end):
                    ed = doc.end()
                else:
                    ed = doc.end
            if not sd or not ed:
                continue
            if (sd - end_date > 0) or (start_date - ed > 0):
                continue

        items.append(proxy)

if not sort_by:
    disp_params = context.REQUEST.SESSION.get('cps_display_params', {})
    sort_by    = disp_params.get('sort_by', 'title');
    direction  = disp_params.get('direction', 'asc');
elif not direction:
    direction = 'asc'

return context.filterContents(items=items,
                              sort_by=sort_by, direction=direction,
                              hide_folder=hide_folder)
