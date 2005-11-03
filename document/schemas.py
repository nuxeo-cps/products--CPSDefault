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
"""CPSDefault custom schemas."""

cpsdefault_search_schema = {
    'SearchableText': {'type': 'CPS String Field', 'data': {}},
    'Title': {'type': 'CPS String Field', 'data': {}},
    'Description': {'type': 'CPS String Field', 'data': {}},
    'Subject': {'type': 'CPS String List Field', 'data': {}},
    'Creator': {'type': 'CPS String Field', 'data': {}},
    'Language': {'type': 'CPS String Field', 'data': {}},
    'modified': {'type': 'CPS String Field', 'data': {}},
    'modified_usage': {'type': 'CPS String Field', 'data': {}},
    'path': {'type': 'CPS String Field', 'data': {}},
    'review_state': {'type': 'CPS String List Field', 'data': {}},
    'portal_type': {'type': 'CPS String List Field', 'data': {}},
    'sort-on': {'type': 'CPS String Field', 'data': {}},
    'sort-order': {'type': 'CPS String Field', 'data': {}},
    'sort-limit': {'type': 'CPS String Field', 'data': {}},
    }


def getSchemas():
    schemas = {
        'cpsdefault_search': cpsdefault_search_schema,
        }
    return schemas
