##parameters=REQUEST=None, query={}, sort_by=None, direction=None, hide_folder=1, folder_prefix=None, start_date=None, end_date=None, allow_empty_search=0, sort_limit=100
# $Id$
""" return a list of proxy matching the query """

from zLOG import LOG, DEBUG


if REQUEST is not None:
    query.update(REQUEST.form)

if str(query.get('modified')) == '1970/01/01':
    del query['modified']
    if query.has_key('modified_usage'):
        del query['modified_usage']

if not allow_empty_search and not query:
    return []

bmt = context.Benchmarktimer('search query %s' % query)

if folder_prefix and not query.has_key('path'):
    query['path'] =  context.getBaseUrl + folder_prefix

# use the cps searchable set to remove objects in 'portal_*' or named '.foo'
query['cps_filter_sets'] = 'searchable'

if hide_folder:
    query['cps_filter_sets'] = {'query' : ('searchable', 'leaves'),
                               'operator' : 'and'}

# XXX TODO make start/end search


# sorting
if sort_by and not query.has_key('sort-on'):
    query['sort-on'] = sort_by
    if direction and not query.has_key('sort-order'):
        if direction.startswith('desc'):
            query['sort-order'] = 'reverse'
    if sort_limit and not query.has_key('sort-limit'):
        query['sort-limit'] = sort_limit

bmt.setMarker('start catalog search for %s')
catalog = context.portal_catalog
brains = catalog(**query)
bmt.setMarker('stop catalog search')

bmt.setMarker('stop')
bmt.saveProfile(context.REQUEST)
# no more need to use filterContents

return brains

