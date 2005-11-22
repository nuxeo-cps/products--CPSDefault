
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
from DateTime import DateTime
from Products.CPSUtil.timer import Timer
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName


# BBB (remove this in CPS-3.6)
from Products.CPSUtil.html import getHtmlBody

##from warnings import warn
##
##warn("The function, "
##     "'Products.CPSDefault.utils.getHtmlBody' "
##     "is a deprecated compatiblity alias for "
##     "'Products.CPSUtil.html.getHtmlBody'; "
##     "please use the new function instead.",
##     DeprecationWarning)

ModuleSecurityInfo('Products.CPSDefault.utils').declarePublic('getHtmlBody')
# END BBB



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
def manageCPSLanguage(context, action, default_language, languages=None):
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


# ------------------------------------------------------------
# Sorting key methods
# XXX hardcoded cpsdefault status order !
STATUS_SORT_ORDER = {'nostate': 0,
                     'pending': 1,
                     'published': 2,
                     'work': 3,
                     }
def id_sortkey(obj):
    """Sort by id."""
    return obj.getId()

def title_sortkey(obj):
    """Sort by title or id."""
    return obj.title_or_id().lower()

def date_sortkey(obj):
    """Sort by modified time."""
    return (obj.modified(), obj.getId())

def effective_sortkey(obj):
    """Sort by effective date."""
    return (obj.getContent().effective(), obj.getId())

def author_sortkey(obj):
    """Sort by creator name."""
    return (obj.Creator(), obj.getId())


module_security.declarePublic('filterContents')
def filterContents(context, items, sort_on=None, sort_order=None,
                   filter_ptypes=None, hide_folder=False):
    """Filter and sort items.

    Remove unauthorize or invalid contents, can filter on portal types and
    folderish content.
    """
    t = Timer('filterContents', level=DEBUG)
    wtool = getToolByName(context, 'portal_workflow')
    ttool = getToolByName(context, 'portal_types')
    now = DateTime()
    if filter_ptypes is None:
        # filter on valid portal types
        filter_ptypes = ttool.objectIds()
    result = []
    display_cache = {}
    t.mark('init')

    for item in items:
        # filter invalid content
        if item.getId().startswith('.'):
            continue
        # filter invalid portal types
        ptype = getattr(item, 'portal_type', None)
        if not (ptype in filter_ptypes):
            continue
        # filter unauthorize contents
        if not _checkPermission('View', item):
            continue
        # filter folderish document
        if hide_folder and item.isPrincipiaFolderish:
            # Using a cache to optimize the retrieval of the
            # 'cps_display_as_document_in_listing' attribute.
            if display_cache.has_key(ptype):
                display_in_listing = display_cache[ptype]
            else:
                display_in_listing = getattr(
                    ttool[ptype], 'cps_display_as_document_in_listing', False)
                display_cache[ptype] = display_in_listing
            if not display_in_listing:
                continue
        # filter non effective or expired published content
        if not _checkPermission('Modify portal content', item):
            review_state = wtool.getInfoFor(item, 'review_state', 'nostate')
            if review_state == 'published':
                doc = item.getContent()
                if now < doc.effective() or now > doc.expires():
                    continue
        result.append(item)
    t.mark('filtering')

    if sort_on is None:
        # no sorting
        t.log()
        return result

    # sorting
    def status_sortkey(obj):
        """Sort by workflow status."""
        global STATUS_SORT_ORDER
        return (STATUS_SORT_ORDER.get(wtool.getInfoFor(obj, 'review_state',
                                                       'nostate'), 9),
                obj.title_or_id().lower())

    make_sortkey = id_sortkey
    if sort_on == 'status':
        make_sortkey = status_sortkey
    elif sort_on == 'date':
        make_sortkey = date_sortkey
    elif sort_on == 'effective':
        make_sortkey = effective_sortkey
    elif sort_on == 'title':
        make_sortkey = title_sortkey
    elif sort_on == 'author':
        make_sortkey = author_sortkey

    result = [(make_sortkey(x), x) for x in result]
    result.sort()
    result = [x[1] for x in result]
    if sort_order.lower().startswith('desc'):
        result.reverse()
    t.log('sorting %s %s' % (sort_on, sort_order or 'asc'))
    return result
