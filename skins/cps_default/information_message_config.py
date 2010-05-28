##parameters=REQUEST=None
"""Returns the rendered form and does the config setting on submit."""

res = {'rendered_form': '',
       'status': '',
       'items': [],
       'items_count': 0,
       'psm': '',
       'valid_form': 0,
       }

from_context = context
# manage form action
if REQUEST is not None:
    form = REQUEST.form
    if form.has_key('search_submit'):
        mapping = form
    else:
        mapping = None
    from_rpath = REQUEST.get('from', None)
    if from_context is not None:
        from_context = context.restrictedTraverse(from_rpath)
else:
    mapping = None

query = {}

ltool = context.portal_layouts
(res['rendered_form'], res['status'], ds) = ltool.renderLayout(
    layout_id='cpsdefault_search', schema_id='cpsdefault_search',
    context=from_context, mapping=mapping, ob=query)

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
