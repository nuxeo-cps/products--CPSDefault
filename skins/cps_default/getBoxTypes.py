## Script (Python) "getBoxTypes"
##parameters=category=None
# $Id$
"""Return  available box types."""

items = [
    {'category': 'basebox',
     'title': 'portal_type_BaseBox_title',
     'desc': 'portal_type_BaseBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_basebox_default'},
               {'provider': 'nuxeo',
                'id': 'separator',
                'desc': 'description_nuxeo_basebox_separator',
                'config': {'title': 'sep'},
                } ,
               {'provider': 'nuxeo',
                'id': 'logo',
                'desc': 'description_nuxeo_basebox_logo'},
               {'provider': 'nuxeo',
                'id': 'search',
                'desc': 'description_nuxeo_basebox_search'},
               {'provider': 'nuxeo',
                'id': 'menu',
                'desc': 'description_nuxeo_basebox_menu'},
               {'provider': 'nuxeo',
                'id': 'breadcrumbs',
                'desc': 'description_nuxeo_basebox_breadcrumbs'},
               {'provider': 'nuxeo',
                'id': 'l10n_select',
                'desc': 'description_nuxeo_basebox_l10n_select'},
               {'provider': 'nuxeo',
                'id': 'footer',
                'desc': 'description_nuxeo_basebox_footer'},
               {'provider': 'nuxeo',
                'id': 'display_settings',
                'desc': 'description_nuxeo_basebox_display_settings'},
               {'provider': 'nuxeo',
                'id': 'folder_header',
                'desc': 'description_nuxeo_basebox_folder_header'},
               {'provider': 'nuxeo',
                'id': 'welcome',
                'desc': 'description_nuxeo_basebox_welcome'},
               ]
     },
    {'category': 'textbox',
     'title': 'portal_type_TextBox_title',
     'desc': 'portal_type_TextBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_textbox_default'},
               ]
     },
    {'category': 'treebox',
     'title': 'portal_type_TreeBox_title',
     'desc': 'portal_type_TreeBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_treebox_default'},
               {'provider': 'nuxeo',
                'id': 'center',
                'desc': 'description_nuxeo_treebox_center',
                'config': {'contextuel': 1,
                           'children_only': 1,
                           'depth': 2,
                           'root': ''}
                },
               ]
     },
    {'category': 'contentbox',
     'title': 'portal_type_ContentBox_title',
     'desc': 'portal_type_ContentBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_contentbox_default'},
               {'provider': 'nuxeo',
                'id': 'last_modified',
                'desc': 'description_nuxeo_contentbox_last_modified',
                'config': {'sort_by': 'date',
                           'direction': 'desc',
                           'query_status': 'published'}
                },
               ]
     },
    {'category': 'actionbox',
     'title': 'portal_type_ActionBox_title',
     'desc': 'portal_type_ActionBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_actionbox_default'},
               {'provider': 'nuxeo',
                'id': 'user',
                'desc': 'description_nuxeo_actionbox_user'},
               ]
     },

    ]

if category:
    for item in items:
        if item['category'] == category:
            return item

return items
