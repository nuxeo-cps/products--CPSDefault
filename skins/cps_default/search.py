##parameters=REQUEST=None, query={}, sort_by=None, direction=None, hide_folder=0, folder_prefix=None, start_date=None, end_date=None, allow_empty_search=0, sort_limit=100
# $Id$
""" return a list of proxy matching the query """

from zLOG import LOG, DEBUG


if REQUEST is not None:
    query.update(REQUEST.form)

for k, v in query.items():
    if not v:
        del query[k]

if str(query.get('modified')) == '1970/01/01':
    del query['modified']
    if query.has_key('modified_usage'):
        del query['modified_usage']

if not allow_empty_search and not query:
    return []

bmt = context.Benchmarktimer('search query %s' % query)

if folder_prefix and not query.has_key('path'):
    query['path'] =  context.getBaseUrl() + folder_prefix

# use the cps searchable set to remove objects in 'portal_*' or named '.foo'
query['cps_filter_sets'] = 'searchable'

if hide_folder:
    query['cps_filter_sets'] = {'query' : ('searchable', 'leaves'),
                                'operator' : 'and'}

# start/end search
if start_date and not query.has_key('start'):
    query['start'] = {'query': start_date,
                      'range': 'min'}
if end_date and not query.has_key('end'):
    query['end'] = {'query': end_date,
                    'range': 'max'}

# sorting
if sort_by and not query.has_key('sort-on'):
    if sort_by in ('title', 'date'):
        sort_by = sort_by.capitalize()
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
