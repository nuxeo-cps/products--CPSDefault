## Script (Python) "getBoxesStyles"
##parameters=type=None
# $Id$
"""Return  available boxes style and format."""

types = [
    {'type': 'basebox',
     'title': 'portal_type_BaseBox_title',
     'desc': 'portal_type_BaseBox_description',
     'fmt': [{'style': 'nuxeo',
              'format': 'default',
              'desc': 'description_nuxeo_basebox_default'},
             {'style': 'nuxeo',
              'format': 'logo',
              'desc': 'description_nuxeo_basebox_logo'},
             {'style': 'nuxeo',
              'format': 'search',
              'desc': 'description_nuxeo_basebox_search'},
             {'style': 'nuxeo',
              'format': 'menu',
              'desc': 'description_nuxeo_basebox_menu'},
             {'style': 'nuxeo',
              'format': 'breadcrumbs',
              'desc': 'description_nuxeo_basebox_breadcrumbs'},
             {'style': 'nuxeo',
              'format': 'l10n_select',
              'desc': 'description_nuxeo_basebox_l10n_select'},
             {'style': 'nuxeo',
              'format': 'footer',
              'desc': 'description_nuxeo_basebox_footer'},
             {'style': 'nuxeo',
              'format': 'display_settings',
              'desc': 'description_nuxeo_basebox_display_settings'},
             {'style': 'nuxeo',
              'format': 'folder_header',
              'desc': 'description_nuxeo_basebox_folder_header'},
             ]
     },
    {'type': 'textbox',
     'title': 'portal_type_TextBox_title',
     'desc': 'portal_type_TextBox_description',
     'fmt': [{'style': 'nuxeo',
              'format': 'default',
              'desc': 'description_nuxeo_textbox_default'},
             ]
     },
    {'type': 'treebox',
     'title': 'portal_type_TreeBox_title',
     'desc': 'portal_type_TreeBox_description',
     'fmt': [{'style': 'nuxeo',
              'format': 'default',
              'desc': 'description_nuxeo_treebox_default'},
             {'style': 'nuxeo',
              'format': 'center',
              'desc': 'description_nuxeo_treebox_center',
              'config': {'contextuel': 1,
                         'children_only': 1,
                         'depth': 2,
                         'root': ''}
              },
             ]
     },
    {'type': 'contentbox',
     'title': 'portal_type_ContentBox_title',
     'desc': 'portal_type_ContentBox_description',
     'fmt': [{'style': 'nuxeo',
              'format': 'default',
              'desc': 'description_nuxeo_contentbox_default'},
             {'style': 'nuxeo',
              'format': 'center',
              'desc': 'description_nuxeo_contentbox_center'},
             {'style': 'nuxeo',
              'format': 'last_modified',
              'desc': 'description_nuxeo_contentbox_last_modified',
              'config': {'sort_by': 'date',
                         'direction': 'desc',
                         'query_status': 'published'}
              },
             ]
     },
    {'type': 'actionbox',
     'title': 'portal_type_ActionBox_title',
     'desc': 'portal_type_ActionBox_description',
     'fmt': [{'style': 'nuxeo',
              'format': 'default',
              'desc': 'description_nuxeo_actionbox_default'},
             {'style': 'nuxeo',
              'format': 'user',
              'desc': 'description_nuxeo_actionbox_user'},
             ]
     },

    ]

if type:
    for t in types:
        if t['type'] == type:
            return t

return types
