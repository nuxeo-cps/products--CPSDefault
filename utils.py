# -*- coding: iso-8859-15 -*-
# (C) Copyright 2003-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
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
"""Miscellaneous utility functions.
"""

from AccessControl import allow_type, allow_class
from AccessControl import ModuleSecurityInfo
from zLOG import LOG, INFO, DEBUG
import re

# This regexp is for path of the following forms :
# /cps/workspaces/cores/myDoc/view
# /cps/workspaces/cores/myDoc/archivedRevision/1/view
# /cps/workspaces/cores/myDoc/archivedRevision/1/archivedRevision/2/view
archived_revision_url_regexp = re.compile('/archivedRevision/\d+')


# Allowing the methods of this file to be imported in restricted code
ModuleSecurityInfo('Products.CPSDefault.utils').declarePublic('getNonArchivedVersionContextUrl')
def getNonArchivedVersionContextUrl(content_url):
    """
    getNonArchivedVersionContextUrl
    """
    # Removing any matched '/archivedRevision/\d+' if present
    content_url = re.sub(archived_revision_url_regexp, '', content_url)

    return content_url


# FIXME: LocalyzerGeddon
ModuleSecurityInfo('Products.CPSDefault.utils').declarePublic('manageCPSLanguage')
def manageCPSLanguage(context, action, default_language, languages):
    """Manage available a languages in a CPS portal with Localizer"""

    catalogs = context.Localizer.objectValues()
    catalogs.append(context.Localizer)
    portal = context.portal_url.getPortalObject()

    if languages is None:
        languages = []
    elif not isinstance(languages, list):
        languages = [languages]

    if not languages and action in ('add', 'delete'):
        psm = 'psm_language_error_select_at_least_one_item'

    elif action == 'add':
        # Make languages available in Localizer
        for lang in languages:
            for catalog in catalogs:
                catalog.manage_addLanguage(lang)

        # XXX needs a tools to register po files for domains
        # Update Localizer/default only !
        i18n_method = getattr(portal,'i18n Updater')
        i18n_method()
        psm = 'psm_language_added'

    elif action == 'delete':
        # Make unavailable languages in Localizer
        for catalog in catalogs:
            catalog.manage_delLanguages(languages)
        psm = 'psm_language_deleted'

    elif action == 'chooseDefault':
        for catalog in catalogs:
            catalog.manage_changeDefaultLang(default_language)
        psm = 'psm_default_language_set'

    else:
        psm = ''

    return psm
