##parameters=
# $Id$
"""Return CPSDefault forms layouts."""

cpsdefault_search_layout = {
    'widgets': {
        'ZCText': {
            'type': 'Search ZCText Widget',
            'data': {
                'fields': ['SearchableText', 'Title', 'Description'],
                'is_i18n': 1,
                'label_edit': 'label_searchadv_full_text',
                },
            },
        'Subject': {
            'type': 'MultiSelect Widget',
            'data': {
                'fields': ['Subject'],
                'is_i18n': 1,
                'label_edit': 'label_subject',
                'vocabulary': 'subject_voc',
                'size': 4,
                'translated': 1,
                },
            },
        'portal_type': {
            'type': 'MultiSelect Widget',
            'data': {
                'fields': ['portal_type'],
                'is_i18n': 1,
                'label_edit': 'label_search_portal_type',
                'vocabulary': 'search_portal_type_voc',
                'size': 4,
                },
            },
        'review_state': {
            'type': 'Select Widget',
            'data': {
                'fields': ['review_state'],
                'is_i18n': 1,
                'label_edit': 'label_search_status',
                'vocabulary': 'search_review_state_voc',
                'translated': 0,
                },
            },
        'modified': {
            'type': 'Search Modified Widget',
            'data': {
                'fields': ['modified'],
                'is_i18n': 1,
                'label_edit': 'label_searchadv_updated',
                },
            },
        'Language': {
            'type': 'Search Language Widget',
            'data': {
                'fields': ['Language'],
                'is_i18n': 1,
                'label_edit': 'label_language',
                },
            },
        'path': {
            'type': 'Search Location Widget',
            'data': {
                'fields': ['path'],
                'is_i18n': 1,
                'label_edit': 'label_search_location',
                },
            },
        },
    'layout': {
        'style_prefix': 'layout_default_',
        'rows': [[{'widget_id': 'ZCText'}, ],
                 [{'widget_id': 'Subject'}, {'widget_id': 'portal_type'}],
                 [{'widget_id': 'modified'}, {'widget_id': 'review_state'}],
                 [{'widget_id': 'path'}, ],
                 [{'widget_id': 'Language'}, ],
                ],
        }
    }

return {'cpsdefault_search': cpsdefault_search_layout,
        }
