##parameters=
# $Id$
"""Return CPSDefault forms schemas."""

cpsdefault_search_schema = {
    'SearchableText': {'type': 'CPS String Field', 'data': {}},
    'Title': {'type': 'CPS String Field', 'data': {}},
    'Description': {'type': 'CPS String Field', 'data': {}},
    'Subject': {'type': 'CPS String List Field', 'data': {}},
    'Creator': {'type': 'CPS String Field', 'data': {}},
    'Language': {'type': 'CPS String Field', 'data': {}},
    'modified': {'type': 'CPS String Field', 'data': {}},
    'modified_usage': {'type': 'CPS String Field',
                       'data': {'default_expr': 'string:range:min'}},
    'folder_prefix': {'type': 'CPS Int Field',
                      'data': {'default_expr': 'python:0',}},
    'review_state': {'type': 'CPS String List Field', 'data': {}},
    'portal_type': {'type': 'CPS String List Field', 'data': {}},
    'sort-on': {'type': 'CPS String Field', 'data': {}},
    'sort-order': {'type': 'CPS String Field', 'data': {}},
    'sort-limit': {'type': 'CPS String Field', 'data': {}},
    }

return {
    'cpsdefault_search': cpsdefault_search_schema,
    }
