##parameters=query={}, sort_by=None, direction=None, hide_folder=0, folder_prefix=None, start_date=None, end_date=None, allow_empty_search=0, sort_limit=100, REQUEST=None
# $Id$
"""Return a list of brains matching the query."""
from zLOG import LOG, DEBUG, INFO

catalog = context.portal_catalog

if REQUEST is not None:
    query.update(REQUEST.form)

for k, v in query.items():
    if not v or same_type(v, []) and not filter(None, v):
        del query[k]

if str(query.get('modified')) == '1970/01/01':
    del query['modified']
    if query.has_key('modified_usage'):
        del query['modified_usage']

if not allow_empty_search and not query:
    return []

# scope of search
if folder_prefix:
    if not query.has_key('path'):
        portal_path = '/' + catalog.getPhysicalPath()[1] + '/'
        query['path'] =  portal_path + folder_prefix
    
    if query.has_key('search_relative_path'):
        current_depth = len(folder_prefix.split('/')) + 1 
        query['relative_path_depth'] = current_depth

if query.has_key('folder_prefix'):
    del query['folder_prefix']

# use filter set to remove objects inside 'portal_*' or named '.foo'
query['cps_filter_sets'] = 'searchable'
if hide_folder:
    query['cps_filter_sets'] = {'query' : ('searchable', 'leaves'),
                                'operator' : 'and'}

# title search
if query.has_key('Title'):
    # we search on the ZCTextIndex,
    # Title index is a FieldIndex only used for sorting
    query['ZCTitle'] = query['Title']
    del query['Title']

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
        sort_by = sort_by.capitalize()  # for compatibility
    elif sort_by == 'status':
        sort_by = 'review_state'
    elif sort_by == 'author':
        sort_by = 'Creator'
    query['sort-on'] = sort_by
    if direction and not query.has_key('sort-order'):
        if direction.startswith('desc'):
            query['sort-order'] = 'reverse'
    if sort_limit and not query.has_key('sort-limit'):
        query['sort-limit'] = sort_limit

bmt = context.Benchmarktimer('search chrono')
LOG('CPSDefault.search', DEBUG, 'start catalog search for %s' % query)
bmt.setMarker('start')
try:
    brains = catalog(**query)
except: # XXX catch only ParseError
    LOG('CPSDefault.search', INFO, 'got an exception during search %s' % query)
    return []
bmt.setMarker('stop')
LOG('CPSDefault.search', DEBUG, 'found %s items in %7.3fs' % (
    len(brains), bmt.timeElapsed('start', 'stop')))

# no more need to use filterContents

return brains
