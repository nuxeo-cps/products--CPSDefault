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

import re
from zLOG import LOG, INFO, DEBUG

from Acquisition import aq_base
from AccessControl import getSecurityManager
from AccessControl import ModuleSecurityInfo

# This regexp is for path of the following forms :
# /cps/workspaces/cores/myDoc/view
# /cps/workspaces/cores/myDoc/archivedRevision/1/view
# /cps/workspaces/cores/myDoc/archivedRevision/1/archivedRevision/2/view
archived_revision_url_regexp = re.compile('/archivedRevision/\d+')


module_security = ModuleSecurityInfo('Products.CPSDefault.utils')


# Allowing the methods of this file to be imported in restricted code
module_security.declarePublic('getNonArchivedVersionContextUrl')
def getNonArchivedVersionContextUrl(content_url):
    """
    getNonArchivedVersionContextUrl
    """
    # Removing any matched '/archivedRevision/\d+' if present
    content_url = re.sub(archived_revision_url_regexp, '', content_url)

    return content_url


# FIXME: LocalizerGeddon
module_security.declarePublic('manageCPSLanguage')
def manageCPSLanguage(context, action, default_language, languages):
    """Manage available a languages in a CPS portal with Localizer"""

    #XXX: Replace with TranslationService
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
        LOG("CPSDefault.utils languages to delete", DEBUG,
            repr(languages))
        LOG("CPSDefault.utils languages available", DEBUG,
            repr(context.Localizer.get_languages_map()))
        LOG("CPSDefault.utils do we delete all available languages ?", DEBUG,
            repr(len(languages) == len(context.Localizer.get_languages_map())))
        if len(languages) == len(context.Localizer.get_languages_map()):
            psm = 'psm_language_error_let_at_least_one_language_to_portal'
        else:
            # Make unavailable languages in Localizer
            for catalog in catalogs:
                catalog.manage_delLanguages(languages)
            psm = 'psm_language_deleted'

    elif action == 'chooseDefault':
        for catalog in catalogs:
            catalog.manage_changeDefaultLang(default_language)
        psm = 'psm_default_language_set'

    else:
        psm = 'psm_language_error_unknown_command'

    return psm



module_security.declarePublic('computeContributors')
def computeContributors(portal, contributors):
    """Compute a new Contributors value.

    Get the current users's full name, and add it to the list of
    contributors if it's not already present.

    Used by a write expression for the Contributors field of the
    metadata schema.
    """
    contributors = list(contributors or ())

    user = getSecurityManager().getUser()
    user_id = user.getId()

    # Find the user's title field in the appropriate directory
    if getattr(aq_base(user), '_aclu', None) is not None:
        # Special fast case for CPSUserFolder
        title_field = user._aclu._getUsersDirectory().title_field
        fullname = user.getProperty(title_field, None)
    else:
        # To get proper computed attributes, we need to ask the
        # entry directly from the directory
        try:
            dir = portal.portal_directories.members
            fullname = dir._getEntry(user_id)[dir.title_field]
        except (AttributeError, KeyError):
            fullname = None

    if not fullname:
        fullname = user_id

    if fullname is not None and fullname not in contributors:
        contributors.append(fullname)

    return contributors
