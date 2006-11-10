##parameters=query={}, sort_by=None, direction=None, hide_folder=False, folder_prefix=None, start_date=None, end_date=None, default_languages=False, allow_empty_search=False, sort_limit=100, REQUEST=None
# $Id$
"""
Return a list of brains matching the query.

Examples:

# Get all the News Item documents in the portal
brains = portal.search(query={'portal_type': ('News Item',)})
for brain in brains:
    proxy = brain.getObject()
    document = proxy.getContent()
    ...

# Get all the Italian News Item and Italian Press Release documents
# in the portal
brains = portal.search(query={'portal_type': ('News Item', 'Press Release'),
                              'Languages': 'it'})

# Get all the published News Item documents in the portal which contains the
# text "mycomparny.com".
brains = portal.search(query={'SearchableText': 'mycompany.com',
                              'portal_type': ('News Item',),
                              'review_state': 'published',
                       }
                      )

# Get all the documents in the portal which are located below the folder
# "folder1" which is located in the "workspaces" folder.
brains = portal.search(query={'path': '/cps/workspaces/folder1'})
# if you know only the relative path:
brains = portal.search(folder_prefix='workspaces/folder1',
                       allow_empty_search=True,
                      )

# the 2 previous searches will return all the documents that are pointed by
# proxies that are located below the folder1,
# this means that if you have a proxy that contains 3 translations you
# will have 3 brains for this proxy.
# If you want only a list of proxies in their default languages without
# the available translation:
brains = portal.search(query={'path': '/cps/workspaces/folder1'},
                       default_languages=True)

Relative path, absolute path and parent (or container) path
-----------------------------------------------------------

To put location constraints in your query you can use any of those parameters in
the query :

- path (absolute, PathIndex)

  This will return all the objects located at the given path or all the way
  below. This is due to the fact that this field is a special PathIndex field.

  The given value must be an absolute path.

- relative_path (relative, FieldIndex)

  This will return all the objects located precisely at the given path.

  The given value must be a relative path.

- container_path (absolute, FieldIndex)

  This will return all the objects located precisely below the given path.

  The given value must be an absolute path.

Note that you can pass the folder_prefix parameter to the search script, but not
in the query. folder_prefix is equivalent to path, but expressed as a relative
path.

More generally, you can put in the query any of the available indexes registered
in the catalog. You can find all the available indexes in the ZMI :
http://localhost:8080/cps/portal_catalog/manage_catalogIndexes

More docs about the use of the ZCatalog can be found here :

- http://www.zope.org/Documentation/How-To/ZCatalogTutorial
- http://www.zope.org/Members/Zen/howto/AdvZCatalogSearching
"""

from zLOG import LOG, DEBUG, INFO
from Products.ZCTextIndex.ParseTree import ParseError
ParseErrors = (ParseError,)
try:
    from Products.TextIndexNG2.BaseParser import QueryParserError
    ParseErrors += (QueryParserError,)
except ImportError:
    pass


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
    LOG('CPSDefault.search', DEBUG, 'No query provided => no answers')
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

if query.has_key('search_relative_path'):
    del query['search_relative_path']

# use filter set to remove objects inside 'portal_*' or named '.foo'
query['cps_filter_sets'] = {'query': ['searchable'],
                            'operator': 'and'}
if default_languages:
    query['cps_filter_sets']['query'].append('default_languages')
if hide_folder:
    query['cps_filter_sets']['query'].append('leaves')

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

bmt = getattr(context.portal_url.getPortalObject(), 'Benchmarktimer', None)
if bmt is not None:
    bmt = bmt('search chrono')
    LOG('CPSDefault.search', DEBUG, 'start catalog search for %s' % query)
    bmt.setMarker('start')
try:
    brains = catalog(**query)
except ParseErrors:
    LOG('CPSDefault.search', INFO, 'got an exception during search %s' % query)
    return []

if bmt is not None:
    bmt.setMarker('stop')
    LOG('CPSDefault.search', DEBUG, 'found %s items in %7.3fs' % (
        len(brains), bmt.timeElapsed('start', 'stop')))

# no more need to use filterContents

return brains
