# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# Benoit Delbosc <ben@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""CPSDefault custom layouts."""

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
                'vocabulary': 'search_portal_type',
                'size': 4,
                },
            },
        'review_state': {
            'type': 'Select Widget',
            'data': {
                'fields': ['review_state'],
                'is_i18n': 1,
                'label_edit': 'label_search_status',
                'vocabulary': 'search_review_state',
                'translated': 0,
                },
            },
        'modified': {
            'type': 'Search Modified Widget',
            'data': {
                'fields': ['modified', 'modified_usage'],
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
        'sort_by': {
            'type': 'Search Sort Widget',
            'data': {
                'fields': ['sort-on', 'sort-order', 'sort-limit'],
                'is_i18n': 1,
                'label_edit': 'label_searchadv_sort_by',
                'sort_limit': 100,
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
                 [{'widget_id': 'sort_by'}, ],
                ],
        }
    }


def getLayouts():
    layouts = {
        'cpsdefault_search': cpsdefault_search_layout,
        }
    return layouts
