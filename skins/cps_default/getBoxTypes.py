##parameters=category=None
# $Id$
"""
Return available box types.
"""

items = [
    {'category': 'basebox',
     'title': 'portal_type_BaseBox_title',
     'desc': 'portal_type_BaseBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_basebox_default'},
               {'provider': 'nuxeo',
                'id': 'hr_separator',
                'desc': 'description_nuxeo_basebox_hr_separator',
                'config': {'title': 'hr_sep'},
                } ,
               {'provider': 'nuxeo',
                'id': 'br_separator',
                'desc': 'description_nuxeo_basebox_br_separator',
                'config': {'title': 'br_sep'},
                } ,
               {'provider': 'nuxeo',
                'id': 'logo',
                'desc': 'description_nuxeo_basebox_logo'},
               {'provider': 'nuxeo',
                'id': 'search',
                'desc': 'description_nuxeo_basebox_search'},
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
                'id': 'conformance_statement',
                'desc': 'description_nuxeo_basebox_conformance_statement'},
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
                'config': {'contextual': 1,
                           'children_only': 1,
                           'depth': 2,
                           'root': '',
                           'authorized_only': 1,
                           'display_managers': 0,
                           'show_root': 1}
                },
               {'provider': 'nuxeo',
                'id': 'sitemap',
                'desc': 'description_nuxeo_treebox_sitemap',
                'config': {'authorized_only': 1,
                           },
                },
               {'provider': 'nuxeo',
                'id': 'sitemap_adv',
                'desc': 'description_nuxeo_treebox_sitemap_adv',
                },
               {'provider': 'nuxeo',
                'id': 'menu',
                'desc': 'description_nuxeo_basebox_menu',
                'config': {'authorized_only': 1,
                           'depth': 1,
                           'show_root': 1,
                           },
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
                'id': 'simple',
                'desc': 'description_nuxeo_contentbox_simple'},
               {'provider': 'nuxeo',
                'id': 'last_modified',
                'desc': 'description_nuxeo_contentbox_last_modified',
                'config': {'sort_by': 'date',
                           'direction': 'desc',
                           'query_status': 'published'}
                },
               {'provider': 'nuxeo',
                'id': 'pending',
                'desc': 'description_nuxeo_contentbox_pending',
                'config': {'sort_by': 'date',
                           'direction': 'asc',
                           'query_status': 'pending'}
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
               {'provider': 'nuxeo',
                'id': 'menu',
                'desc': 'description_nuxeo_actionbox_menu'},
               {'provider': 'nuxeo',
                'id': 'header',
                'desc': 'description_nuxeo_actionbox_header'},
               ]
     },
    {'category': 'imagebox',
     'title': 'portal_type_ImageBox_title',
     'desc': 'portal_type_ImageBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_imagebox_default'},
               ]
     },
    {'category': 'flashbox',
     'title': 'portal_type_FlashBox_title',
     'desc': 'portal_type_FlashBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_flashbox_default'},
               ]
     },
    {'category': 'eventcalendarbox',
     'title': 'portal_type_EventCalendarBox_title',
     'desc': 'portal_type_EventCalendarBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_basebox_calendar'},
               ]
     },
    {'category': 'internallinksbox',
     'title': 'portal_type_InternalLinksBox_title',
     'desc': 'portal_type_InternalLinksBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_internallinks_default'},
               ]
     },
    {'category': 'docrenderbox',
     'title': 'portal_type_DocRenderBox_title',
     'desc': 'portal_type_DocRenderBox_description',
     'types': [{'provider': 'nuxeo',
                'id': 'default',
                'desc': 'description_nuxeo_render_default'},
              ]
     },
    ]

citems = context.getCustomBoxTypes()

for citem in citems:
    found = 0
    for item in items:
        if item['category'] == citem['category']:
            item['types'].extend(citem['types'])
            found = 1
            break
    if not found:
        items.append(citem)

if category:
    found = None
    for item in items:
        if item['category'] == category:
            found = item
            break
    return found

return items
