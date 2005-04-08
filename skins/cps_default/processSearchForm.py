##parameters=REQUEST
# $Id$
"""Return the rendered search form and do the search on submit."""

res = {'rendered_form': '',
       'status': '',
       'items': [],
       'items_count': 0,
       'psm': '',
       'valid_form': 0,
       }

# manage form action
form = REQUEST.form
if form.has_key('search_submit'):
    mapping = form
else:
    mapping = None

query = {}

ltool = context.portal_layouts
(res['rendered_form'], res['status'], ds) = ltool.renderLayout(
    layout_id='cpsdefault_search', schema_id='cpsdefault_search',
    context=context, mapping=mapping, ob=query)

if mapping is not None:
    # search
    if res['status'] == 'valid':
        res['items'] = context.search(query=query)
        res['valid_form'] = 1
    else:
        res['psm'] = 'psm_content_error'
        #raise '%s invalid ' % res['status'] + str(ds.getErrors())
    res['items_count'] = len(res['items'])

return res
