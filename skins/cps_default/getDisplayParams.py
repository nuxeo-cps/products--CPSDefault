## Script (Python) "getDisplayParams"
##parameters=format=None, sort_by=None, columns=None, items_per_page=None, nav_action=None, nb_items=None
# $Id$
""" return params for display_content macro """

cps_pref = context.REQUEST.SESSION.get('cps_display_params', {})

def_params = {'format': 'detail',
              'sort_by': 'title',
              'items_per_page': 10,
              'nav_action': 'folder_view',
              }

params = def_params

if format:
    params['format'] = format
else:
    params['format'] = cps_pref.get('format', def_params['format'])

if sort_by:
    params['sort_by'] = sort_by
else:
    params['sort_by'] = cps_pref.get('sort_by', def_params['sort_by'])

if nav_action:
    params['nav_action'] = nav_action

if columns:
    params['columns'] = columns
else:
    fmt = params['format']
    if fmt == 'icon':
        col = 5
    elif fmt == 'compact':
        col = 2
    elif fmt == 'detail':
        col = 1
    else:
        col = 2
    params['columns'] = col

if items_per_page:
    params['items_per_page'] = items_per_page
params['items_per_page'] = min(nb_items, params['items_per_page'])


return params
