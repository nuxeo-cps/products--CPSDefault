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
                'size': 3,
                },
            },
        'review_state': {
            'type': 'Generic MultiSelect Widget',
            'data': {
                'fields': ['review_state'],
                'is_i18n': 1,
                'label_edit': 'label_review_state',
                'vocabulary': 'review_state_voc',
                'render_format': 'checkbox',
                'translated': 1,
                'size': 3,
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
        },
    'layout': {
        'style_prefix': 'layout_default_',
        'rows': [[{'widget_id': 'ZCText'}, ],
                 [{'widget_id': 'Subject'}, {'widget_id': 'review_state'}],
                 [{'widget_id': 'modified'}, ],
                 [{'widget_id': 'Language'}, ],
                ],
        }
    }

return {'cpsdefault_search': cpsdefault_search_layout,
        }
