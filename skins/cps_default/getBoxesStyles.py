## Script (Python) "getBoxesStyles"
##parameters=type=None
# $Id$
"""Return the available boxes style and format."""
# XXX TODO i18n / l10n

types = [
    {'type': 'basebox',
     'desc': 'Generic box',
     'fmt': [{'style': 'nuxeo',
              'format': 'default',
              'desc': 'an empty default box'},
             {'style': 'nuxeo',
              'format': 'logo',
              'desc': 'a top rigth nuxeo logo'},
             {'style': 'nuxeo',
              'format': 'search',
              'desc': 'a top left search box'},
             {'style': 'nuxeo',
              'format': 'menu',
              'desc': 'a top menu displaying 2 levels of sections and root of workspaces'},
             {'style': 'nuxeo',
              'format': 'breadcrumbs',
              'desc': 'a breadcrumbs bar'},
             {'style': 'nuxeo',
              'format': 'l10n_select',
              'desc': 'a locale selector'},
             {'style': 'nuxeo',
              'format': 'footer',
              'desc': 'a nuxeo footer'},
             ]
     },
    {'type': 'textbox',
     'desc': 'Display static text',
     'fmt': [{'style': 'nuxeo',
                  'format': 'default',
                  'desc': 'default box'},
                 ]
     },
    {'type': 'treebox',
     'desc': 'Display list of folders in a tree-like format',
     'fmt': [{'style': 'nuxeo',
              'format': 'default',
              'desc': 'box format'},
             {'style': 'nuxeo',
              'format': 'center',
              'desc': 'long format'},
             ]
     },
    {'type': 'contentbox',
     'desc': 'Display list of documents',
     'fmt': [{'style': 'nuxeo',
                  'format': 'default',
                  'desc': 'box format'},
                 {'style': 'nuxeo',
                  'format': 'center',
                  'desc': 'long format'},
                 ]
     },
    {'type': 'actionbox',
     'desc': 'Display actions list',
     'fmt': [{'style': 'nuxeo',
                  'format': 'default',
                  'desc': 'box format'},
                 {'style': 'nuxeo',
                  'format': 'user',
                  'desc': 'user box information'},
                 ]
     },

    ]

if not type:
    return types

for t in types:
    if t['type'] == type:
        return t

return
