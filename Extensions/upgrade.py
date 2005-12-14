# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
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

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
from zLOG import LOG, DEBUG, INFO

TYPES = ('Workspace', 'Section', 'CPSForum')
CHECK_ROOTS = ('workspaces', 'sections')

def checkUpgradeWorkflows(context):
    """Check if workflows need to be upgraded."""
    upgrade = 0
    portal = getToolByName(context, 'portal_url').getPortalObject()
    for rpath in CHECK_ROOTS:
        ob = portal.restrictedTraverse(rpath, default=None)
        if ob is None:
            continue
        workflow_history = getattr(aq_base(ob), 'workflow_history', None)
        if workflow_history is None:
            continue
        for wf_id, wfh in workflow_history.items():
            if not wfh:
                continue
            status = wfh[-1]
            if status.has_key('review_state'):
                continue
            LOG('checkUpgradeWorkflows', INFO,
                "Workflow status for '%s' needs to be upgraded." % rpath)
            upgrade = 1
            break
    return upgrade

def upgradeWorkflows(self):
    """Upgrade the folders after workflow change.

    This script is to be launched as an ExternalMethod, it will search
    for all folder documents present in the portal and fix their
    workflow state.

    How to use the upgradeWorkflowss ExternalMethod:
    - Log into the ZMI as manager
    - Go to your CPS root directory
    - Create an External Method with the following parameters:

    id            : upgradeWorkflows
    title         : Use this method if you upgrade an instance older
                    than CPS 3.2.1
    Module Name   : CPSDefault.upgrade
    Function Name : upgradeWorkflows

    - save it
    - then click on the test tab of this external method
    """

    log_key = 'upgradeWorkflows'
    LOG(log_key, DEBUG, "")

    nchanged = 0
    brains = self.portal_catalog.searchResults(portal_type=TYPES)
    for brain in brains:
        ob = brain.getObject()
        if ob is None:
            continue
        workflow_history = getattr(aq_base(ob), 'workflow_history', None)
        if workflow_history is None:
            continue
        changed = 0
        for wf_id, wfh in workflow_history.items():
            if not wfh:
                continue
            status = wfh[-1]
            if status.has_key('review_state') or not status.has_key('state'):
                continue
            status['review_state'] = status['state']
            del status['state']
            workflow_history._p_changed = 1 # trigger persistence
            changed = 1
        if changed:
            path = '/'.join(ob.getPhysicalPath())
            LOG(log_key, DEBUG, "upgrading %s" % path)
            ob.reindexObject(idxs=['review_state'])
            nchanged += 1
    LOG(log_key, DEBUG, "%s objects upgraded" % nchanged)
    return '%s objects upgraded' % nchanged

def upgradeURLTool(self):
    """Upgrade portal_url

    The CMF URLTool is replaced by the CPS URLTool thta extends it by adding
    methods to deal with virtual hosting
    """
    from Products.CPSCore.URLTool import URLTool
    utool_id = URLTool.id
    portal = self.portal_url.getPortalObject()
    utool = getToolByName(portal, utool_id, None)
    add_it = 0
    if utool is None:
        add_it = 1
    else:
        if utool.meta_type != URLTool.meta_type:
            add_it = 1
            portal.manage_delObjects([utool_id])
    if add_it:
        portal.manage_addProduct['CPSCore'].manage_addTool(URLTool.meta_type)
        log = "portal_url upgraded"
    else:
        log = "portal_url did not need to be upgraded"
    return log


def upgrade_334_335_cache_parameters(context):
    """Upgrades cache parameters.

    - 'no-cache:(contextual)' is added to the Content Portlet
       cache parameters.
    """
    ptltool = getToolByName(context, 'portal_cpsportlets', None)
    if ptltool is None:
        return "This site don't use CPSSkins/CPSPortlets"

    PORTLET_ID = 'Content Portlet'
    NEW_PARAMETER = 'no-cache:(contextual)'

    logger = []
    log = logger.append

    log("Updating portlet cache parameters...")
    # get the current parameters
    params = ptltool.getCacheParametersFor(PORTLET_ID)

    # update the parameters
    if NEW_PARAMETER in params:
        log("  '%s' already set for '%s'." % (NEW_PARAMETER, PORTLET_ID))
    else:
        params.insert(0, NEW_PARAMETER)
        ptltool.updateCacheParameters({PORTLET_ID:params})
        log("  '%s' added to '%s'." % (NEW_PARAMETER, PORTLET_ID))
    return "\n".join(logger)


def upgrade_334_335_clean_catalog(self):
    """Remove None objects out of the catalog

    On some instances between 3.3.4 and 3.3.5, None objects appeared in the
    catalog causing the search result page to crash
    """
    log = "Checking and cleaning cataloged None objects...\n"
    catalog = getToolByName(self, 'portal_catalog')
    docs2unindex = []
    for brain in catalog.search({}):
        try:
            ob = brain.getObject()
        except AttributeError:
            ob = None
        if ob is None:
            id = brain.getPath()
            docs2unindex.append(id)
    for id in docs2unindex:
        LOG('CPSDefault.Extensions.upgrade', INFO, 'Uncataloging: %s' % id)
        catalog.uncatalog_object(id)
    log += "Uncataloged %d None objects" % len(docs2unindex)
    return log

################################################## 3.2.0

def upgrade_320_334(self):
    """Upgrades from 3.2.0"""
    log = []
    dolog = log.append

    from Products.CPSDocument.Extensions.upgrade import upgradeDocuments
    dolog("Upgrading document types")
    upgradeDocuments(self)

    return '\n'.join(log)

################################################## 3.3.5

def upgrade_334_335(self):
    """Upgrades for CPS 3.3.5"""

    # upgrade repository
    from Products.CPSCore.upgrade import upgrade_334_335_repository
    log = upgrade_334_335_repository(self)

    # cleaning the catalog if needed
    log += "\n\n" + upgrade_334_335_clean_catalog(self)

    # upgrade portal_url
    log += "\n\n" + upgradeURLTool(self)

    # upgrade portlet cache parameters
    log += "\n\n" + upgrade_334_335_cache_parameters(self)

    # Upgrade CPSDocument
    from Products.CPSDocument.upgrade import upgrade_334_335_allowct_sections
    log += "\n\n" + upgrade_334_335_allowct_sections(self)

    # Upgrade CPSNewsLetters
    try:
        from Products.CPSNewsLetters.upgrade import \
             upgrade_334_335_allowct_sections
    except ImportError, e:
        if str(e) != 'No module named CPSNewsLetters.upgrade':
            raise
    else:
        log += "\n\n" + upgrade_334_335_allowct_sections(self)

    return log

################################################## 3.3.6

def upgrade_335_336(self):
    """Upgrades for CPS 3.3.6"""
    log = []
    dolog = log.append

    # Upgrade catalog indexes and broken objects with unicode
    from Products.CPSCore.upgrade import upgrade_335_336_catalog
    dolog(upgrade_335_336_catalog(self))

    # Upgrade CPSDocument
    from Products.CPSDocument.upgrade import upgrade_335_336_fix_broken_flexible
    dolog(upgrade_335_336_fix_broken_flexible(self))

    # Upgrade CPSPortlet
    # If within a CPSDefault with portlet interface
    portal = self.portal_url.getPortalObject()
    if getToolByName(portal, 'portal_cpsportlets', None) is not None:
        from Products.CPSPortlets.upgrade import upgrade_335_336_portlets
        from Products.CPSPortlets.upgrade import upgrade_335_336_skins
        dolog(upgrade_335_336_portlets(self))
        dolog(upgrade_335_336_skins(self))

    return '\n'.join(log)

################################################## 3.3.6

def upgrade_336_337(self):
    """Upgrades for CPS 3.3.7"""
    log = []
    dolog = log.append

    # upgrade Flash Animations
    # Upgrade CPSDocument
    from Products.CPSDocument.upgrade import upgrade_336_337_anim_flash
    dolog(upgrade_336_337_anim_flash(self))

    return '\n'.join(log)

################################################## 3.3.8

def upgrade_before_340(self):
    """Upgrades to run before cpsupdate on a 3.4.0"""
    log = []
    dolog = log.append

    ctool = getToolByName(self, 'portal_catalog')
    indexes = ctool.indexes()
    if 'cps_filter_sets' in indexes:
        index = ctool._catalog.getIndex('cps_filter_sets')
        if not index.filteredSets.has_key('nodes'):
            dolog('Reset cps_filter_sets')
            ctool.delIndex('cps_filter_sets')

    return '\n'.join(log)

def upgrade_338_340_portlets(self):
    """Attempts to update portlets to support the boxless setup

    see: http://svn.nuxeo.org/trac/pub/ticket/1161
    """
    logger = []
    log = logger.append
    log('CPSDefault: migrating to the boxless setup: upgrading portlets.')

    from Products.CPSInstaller.CPSInstaller import CPSInstaller
    utool = getToolByName(self, 'portal_url')
    ptltool = getToolByName(self, 'portal_cpsportlets', None)

    portal = utool.getPortalObject()
    installer = CPSInstaller(portal, 'Installer')

    content_well_portlets = (
        {'type': 'Text Portlet',
         'slot': 'content_well',
         'Title': 'Welcome message',
         'text': 'welcome_body',
         'text_format': 'normal',
         'visibility_range': [0, 1],
         'text_position': 'html',
         'i18n': 1,
         'guard': {
             'guard_expr': "python: published == 'index_html'",
             },
        },
        {'type': 'Document Portlet',
         'slot': 'content_well',
         'visibility_range': [1, 0],
         'order': 10,
         'Title': 'Document Portlet',
         'guard': {
             'guard_expr': "python: published == 'folder_view'",
             },
        },
        {'type': 'Navigation Portlet',
         'slot': 'content_well',
         'Title': 'Subfolders',
         'order': 20,
         'visibility_range': [1, 0],
         'display_hidden_folders': False,
         'display': 'subfolder_contents',
         'guard': {
             'guard_expr': "python: published == 'folder_view'",
             },
        },
        # TODO replace the folder contents view with an
        # "Extended folder contents" view to match the nav_content box
        {'type': 'Custom Portlet',
         'slot': 'content_well',
         'order': 30,
         'custom_cache_params': ['no-cache'],
         'render_method': 'portlet_folder_contents',
         'Title': 'Folder contents',
             'guard': {
             'guard_expr': "python: published == 'folder_view'",
             },
        },
    )

    if ptltool is None:
        log("CPSDefault: portlet tool not found. Migration aborted.")

    if ptltool.getPortlets(slot='content_well', override=0, visibility_check=0,
                           guard_check=0):
        log("CPSDefault: portlets have been found in the 'content_well' slot. "
            "Migration aborted")

    installer.verifyPortlets(portlets=content_well_portlets, object=portal)
    log("CPSDefault: portlets replacing boxes have been added to the "
        "'content_well' slot")

    return '\n'.join(logger)

def upgrade_338_340(self):
    """Upgrades for CPS 3.3.8 after cpsupdate"""
    log = []
    dolog = log.append

    # Upgrade CPSPortlet / CPSSkins to a boxless setup
    portal = self.portal_url.getPortalObject()
    if getToolByName(portal, 'portal_cpsportlets', None) is None:
        # TODO: install CPSPortlets ?
        pass

    from Products.CPSPortlets.upgrade import upgrade_338_340_themes
    dolog(upgrade_338_340_themes(self))
    dolog(upgrade_338_340_portlets(self))
    return '\n'.join(log)

################################################## Zope 2.8

def upgrade_catalog_Z28(self):
    """Upgrade portal_catalog because of zcatalog changes
    """
    log = []
    dolog = log.append
    for catalog in (getToolByName(self, 'portal_catalog'),
                    getToolByName(self, 'portal_cpsportlets_catalog', None)):

        if catalog is None:
            continue

        # This upgrades transparently the _catalog._length attr
        len(catalog)

        # Upgrade manually the indexes now
        for idx in catalog.Indexes.objectValues():
            bases = [str(name) for name in idx.__class__.__bases__]
            found = False

            if idx.meta_type  == 'PathIndex':
                found = True
            else:
                for base in bases:
                    if 'UnIndex' in base:
                        found = True
                        break

            if found:
                if not hasattr(idx, '_length'):
                    dolog('ugrade zope 2.7 catalog index')
                    idx._length = idx.__len__
                    delattr(idx, '__len__')

    return '\n'.join(log)


##################

AUTOMATIC_UPGRADES = (
    # format is the following:
    # from, to, upgrade method, do it 'before' or 'after' cpsupdate
    # if `from` is a star (*) the portal version is not changed
    # the list from/to must be contiguous.
    ('*',  'check zope 2.8', upgrade_catalog_Z28, 'before'),
    ('*', 'prepare to 3.4.0', upgrade_before_340, 'before'),
    ('3.2.0', '3.3.4', upgrade_320_334, 'after'),
    ('3.3.4', '3.3.5', upgrade_334_335, 'after'),
    ('3.3.5', '3.3.6', upgrade_335_336, 'after'),
    ('3.3.6', '3.3.7', upgrade_336_337, 'after'),
    ('3.3.7', '3.3.8', None           , 'after'),
    ('3.3.8', '3.4.0', upgrade_338_340, 'after'),
    ('3.3.8.1', '3.4.0', upgrade_338_340, 'after'),
    )

