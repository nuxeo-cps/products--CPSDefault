##parameters=
# $Id$
"""
FIXME: docstring?
"""
if context.isInWorkspace():
    custom_params = {'format': 'detail_tab',
                     'sort_by': None,
                     'direction': 'asc',
                     'items_per_page': 50,
                     'nav_action': 'folder_view',
                     'filter': 0,
                     'detail_tab_columns': ['title', 'type', 'size', 
                                'date', 'author','status', 'version'],
                    }

else:
    custom_params =  {'format': None,
                      'sort_by': None,
                      'direction': 'asc',
                      'items_per_page': 30,
                      'nav_action': 'folder_view',
                      'filter': 0,
                      'detail_tab_columns': ['title', 'type', 'size',
                                'date', 'author', 'status', 'version'],
                     }

return custom_params