##parameters=mapping
# $Id$

res = {'rendered_form': '',
       'status': None,
       'result': None,
       }

# validate form
ltool = context.portal_layouts
res['rendered_form'], res['status'], ds = ltool.renderLayout(
    layout_id='members_search',
    schema_id='members',
    context=context,
    mapping=mapping,
    layout_mode='edit',
    style_prefix='layout_default_')

if res['status'] == 'valid':
    # execute action
    res['result'] = ds.getDataModel()

return res
