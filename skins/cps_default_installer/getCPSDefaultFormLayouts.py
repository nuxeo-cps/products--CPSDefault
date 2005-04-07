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
                'label_edit': 'label_search_resutls_with',
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
                'label_edit': 'label_portal_type',
                'vocabulary': 'search_portal_type_voc',
                'size': 4,
                },
            },
        'review_state': {
            'type': 'Select Widget',
            'data': {
                'fields': ['review_state'],
                'is_i18n': 1,
                'label_edit': 'label_review_state',
                'vocabulary': 'search_review_state_voc',
                'translated': 0,
                },
            },
        'modified': {
            'type': 'Search Modified Widget',
            'data': {
                'fields': ['modified'],
                'is_i18n': 1,
                'label_edit': 'label_search_udpated',
                },
            },
        'Language': {
            'type': 'Search Language Widget',
            'data': {
                'fields': ['Language'],
                'is_i18n': 1,
                'label_edit': 'label_search_language',
                },
            },
        'path': {
            'type': 'Search Location Widget',
            'data': {
                'fields': ['path'],
                'is_i18n': 1,
                'label_edit': 'label_search_path',
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
