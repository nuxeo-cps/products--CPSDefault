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
from zLOG import LOG, INFO, DEBUG, WARNING

from Acquisition import aq_base
from AccessControl import getSecurityManager
from AccessControl import ModuleSecurityInfo
from DateTime import DateTime
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CPSUtil.timer import Timer


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
def id_sortkey(ob):
    """Sort by id."""
    return ob.getId()

def title_sortkey(ob):
    """Sort by title or id."""
    return ob.title_or_id().lower()

def date_sortkey(ob):
    """Sort by modified time."""
    return (ob.modified(), ob.getId())

def effective_sortkey(ob):
    """Sort by effective date."""
    return (ob.getContent().effective(), ob.getId())

def author_sortkey(ob):
    """Sort by creator name."""
    return (ob.Creator(), ob.getId())


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
        if not _checkPermission(View, item):
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
        if not _checkPermission(ModifyPortalContent, item):
            review_state = wtool.getInfoFor(item, 'review_state', 'nostate')
            if review_state == 'published':
                doc = item.getContent()
                if now < doc.effective() or now > doc.expires():
                    continue
        result.append(item)
    t.mark('filtering')

    if sort_on is None:
        # no sorting
        #t.log()
        return result

    # sorting
    def status_sortkey(ob):
        """Sort by workflow status."""
        global STATUS_SORT_ORDER
        return (STATUS_SORT_ORDER.get(wtool.getInfoFor(ob, 'review_state',
                                                       'nostate'), 9),
                ob.title_or_id().lower())

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
    if sort_order in ('desc', 'reverse'):
        result.reverse()
    #t.log('sorting %s %s' % (sort_on, sort_order or 'asc'))
    return result


module_security.declarePublic('getFolderContents')
def getFolderContents(container, sort_on=None, sort_order=None,
                      filter_ptypes=None, hide_folder=False):
    """Get a filtered and sorted container's contents objects."""
    t = Timer('getFolderContents', level=DEBUG)
    ret = filterContents(container, container.objectValues(),
                         sort_on, sort_order, filter_ptypes, hide_folder)
    #t.log('end')
    return ret


module_security.declarePublic('getCatalogFolderContents')
def getCatalogFolderContents(container, filter_ptypes=None, hide_folder=False,
                             sort_on=None, sort_order=None,
                             sort_limit=None, request=None):
    """Get a filtered and sorted container's contents using the catalog.

    Return catalog brains.
    """
    t = Timer('getCatalogFolderContents', level=INFO)
    ctool = getToolByName(container, 'portal_catalog')
    lucene = 'Lucene' in ctool.meta_type
    container_path = '/'.join(container.getPhysicalPath())
    translation_service = getToolByName(container, 'translation_service', None)
    match_languages = 'en'
    if translation_service is not None:
        match_languages = translation_service.getSelectedLanguage()
        if not match_languages:
            if container.isUsePortalDefaultLang():
                match_languages = translation_service.getDefaultLanguage()
    t.mark('init')

    # build query

    # - there is curently no cps_filter_sets in Lucene
    # - match_languages is not part of the standard indexes
    #   its purpose is to make the default language match if
    #   users' doesn't exist in proxy.
    #
    #   it must be registered to the tool like this:
    # CMF Catalog Tool:
    #   <index name="match_languages" meta_type="KeywordIndex">
    #    <indexed_attr value="match_languages"/>
    #   </index>
    # CPS Lucene Catalog Tool:
    #   <field name="match_languages" attr="match_languages"
    #                analyzer="Standard" type="MultiKeyword"/>
    query = {
        'container_path': container_path,
        'cps_filter_sets': 'searchable',
        'match_languages': match_languages,
        } 
    if filter_ptypes is not None:
        query['portal_type'] = filter_ptypes

    if hide_folder:
        query['cps_filter_sets'] = {'query': ('searchable', 'leaves'),
                                    'operator': 'and'}
    user = _getAuthenticatedUser(container)
    query['allowedRolesAndUsers'] = ctool._listAllowedRolesAndUsers(user)
    if 'Manager' in query['allowedRolesAndUsers']:
        # manager powa
        del query['allowedRolesAndUsers']
    if not _checkPermission(AccessInactivePortalContent, container):
        now = DateTime()
        query['effective'] = {'query': now,
                              'range': 'min'}

    if sort_on is not None:
        # compatibility
        if sort_on in ('title', 'date'):
            sort_on = sort_on.capitalize()
            if lucene:
                sort_on += '_sort'
        elif sort_on == 'status':
            sort_on = 'review_state'
        elif sort_on == 'author':
            sort_on = 'Creator'
        query['sort-on'] = sort_on
        if sort_order in ('desc', 'reverse'):
            query['sort-order'] = 'reverse'
        if not lucene and sort_limit is not None:
            # lucene uses is batching capability anyway
            query['sort-limit'] = sort_limit
        elif request is not None:
            b_start = query['b_start'] = int(request.get('b_start', 0))
            b_size = query['b_size'] = 12 # GR arbitrary, I now
        else:
            b_start = query['b_start'] = 0
            b_size = query['b_size'] = 12

    t.mark('build query: %s' % str(query))
    if lucene:
        # XXX obviously one should use the server-side batching, but that means rewriting lots of things
        brains = ctool._search(**query)

        # caching in request so that getBatchItems or the like can decide not to do anything
        if request is not None:
            nb_res = brains and brains[0].out_of or 0
            request['cpslucenecatalog_folder_contents'] = (b_start, b_size, nb_res)
    else:
        brains = ZCatalog.searchResults(ctool, None, **query)
    #t.log('search result: %s docs' % len(brains))
    return brains


module_security.declarePublic('reindexFolderContentPositions')
def reindexFolderContentPositions(container):
    """Reindex when content order is changed."""
    t = Timer('reindexFolderContentPositions', level=INFO)
    if not _checkPermission(ModifyPortalContent, container):
        LOG('reindexPositions', WARNING,
            'Unauthorized call on %s' % container.getPhysicalPath())
        return
    if not hasattr(aq_base(container), 'getObjectPosition'):
        # no positioning
        return
    # reindex position of the 100 hundred first docs
    # this is fine as ordering by hand more than 100 hundred docs is not human
    brains = getCatalogFolderContents(container,
                                      sort_on='position_in_container',
                                      sort_limit=100)
    t.mark('fetch %s brains' % len(brains))
    ctool = getToolByName(container, 'portal_catalog')
    reindex_count = 0
    for brain in brains:
        if not brain.has_key('getId'):
            continue
        ob_id = brain['getId']
        new_position = container.getObjectPosition(ob_id)
        if brain.has_key('position_in_container'):
            old_position = brain['position_in_container']
        else:
            old_position = 0
        if old_position != new_position:
            # only access and reindex objects that have changed their position
            ob = brain.getObject()
            if ob is not None:
                # need to update the metadata to save position_in_container
                ctool.reindexObject(ob, ['position_in_container'],
                                    update_metadata=1)
                reindex_count += 1
            else:
                LOG('reindexPositions', WARNING,
                    'invalid catalog entry: %s' % brain.getPath())
    #t.log('reindex %i objects' % reindex_count)
