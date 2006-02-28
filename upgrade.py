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

def check_upgradeURLTool(portal):
    from Products.CPSCore.URLTool import URLTool
    return not isinstance(getToolByName(portal, 'portal_url'), URLTool)


def upgrade_334_335_portlet_cache_parameters(context, check=False):
    """Upgrades cache parameters.

    - 'no-cache:(contextual)' is added to the Content Portlet
       cache parameters.
    """
    ptltool = getToolByName(context, 'portal_cpsportlets', None)
    if ptltool is None:
        if check:
            return False
        return "This site don't use CPSSkins/CPSPortlets"

    PORTLET_ID = 'Content Portlet'
    NEW_PARAMETER = 'no-cache:(contextual)'

    logger = []
    log = logger.append

    log("Updating portlet cache parameters...")
    # get the current parameters
    try:
        params = ptltool.getCacheParametersFor(PORTLET_ID)
    except AttributeError:
        # ptltool.cache_parameters is missing
        if check:
            return True
        else:
            ptltool.initializeCacheParameters()
            ptltool.resetCacheParameters()
            return "CPSPortlets: Cache parameters initialized"

    # update the parameters
    if NEW_PARAMETER in params:
        if check:
            return False
        log("  '%s' already set for '%s'." % (NEW_PARAMETER, PORTLET_ID))
    else:
        if check:
            return True
        params.insert(0, NEW_PARAMETER)
        ptltool.updateCacheParameters({PORTLET_ID:params})
        log("  '%s' added to '%s'." % (NEW_PARAMETER, PORTLET_ID))
    return "\n".join(logger)

def check_upgrade_334_335_portlet_cache_parameters(portal):
    return upgrade_334_335_portlet_cache_parameters(portal, check=True)


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
        except (AttributeError, KeyError):
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

def upgrade_320_334_document_types(portal, check=False):
    """Upgrade various documents to new portal_types or new schemas.
    """
    res = _modifyPortalType(portal, 'News', 'News Item', check)
    if check and res:
        return True
    res = _modifyPortalType(portal, 'PressRelease', 'Press Release', check)
    if check:
        return res

    ttool = getToolByName(portal, 'portal_types')
    for portal_type in ('News', 'PressRelease'):
        if portal_type in ttool.objectIds():
            ttool.manage_delObjects(portal_type)

    return "Upgraded document types News and PressRelease"

def _modifyPortalType(portal, old, new, check=False):
    log_key = 'modifyPortalType'
    catalog = getToolByName(portal, 'portal_catalog')
    brains = catalog.searchResults(portal_type=old)

    if check:
        return bool(len(brains))
    for brain in brains:
        proxy = brain.getObject()
        LOG(log_key, DEBUG, "checking %s..." % proxy.title_or_id)
        for lang in proxy.getProxyLanguages():
            doc = proxy.getContent(lang=lang)
            if doc.portal_type == 'News':
                # Change the newsdate field into EffectiveDate
                newsdate = doc.__dict__.get('newsdate')
                if newsdate is not None:
                    LOG(log_key, DEBUG, "updating %s" % proxy.title_or_id)
                    doc.setEffectiveDate(newsdate)
                    delattr(doc, 'newsdate')
            doc.portal_type = new
        proxy.portal_type = new
        proxy.reindexObject()

def check_upgrade_320_334_document_types(portal):
    return upgrade_320_334_document_types(portal, check=True)

def upgrade_320_334(self):
    """Upgrades from 3.2.0"""
    log = []
    dolog = log.append
    dolog("Upgrading document types")
    upgrade_320_334_document_types(self)
    return '\n'.join(log)

################################################## 3.3.5

def upgrade_334_335(self):
    """Upgrades for CPS 3.3.5"""

    # upgrade repository
    from Products.CPSCore.upgrade import upgrade_334_335_repository_security
    log = upgrade_334_335_repository_security(self)

    # cleaning the catalog if needed
    log += "\n\n" + upgrade_334_335_clean_catalog(self)

    # upgrade portal_url
    log += "\n\n" + upgradeURLTool(self)

    # upgrade portlet cache parameters
    log += "\n\n" + upgrade_334_335_portlet_cache_parameters(self)

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
    from Products.CPSCore.upgrade import upgrade_335_336_catalog_unicode
    dolog(upgrade_335_336_catalog_unicode(self))

    # Upgrade CPSDocument
    from Products.CPSDocument.upgrade import upgrade_335_336_fix_broken_flexible
    dolog(upgrade_335_336_fix_broken_flexible(self))

    # Upgrade CPSPortlet
    # If within a CPSDefault with portlet interface
    portal = self.portal_url.getPortalObject()
    if getToolByName(portal, 'portal_cpsportlets', None) is not None:
        from Products.CPSPortlets.upgrade import upgrade_335_336_portlets_catalog
        from Products.CPSPortlets.upgrade import upgrade_335_336_skins
        dolog(upgrade_335_336_portlets_catalog(self))
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

def upgrade_before_340(self, check=False):
    """Upgrades to run before cpsupdate on a 3.4.0.
    """
    log = []
    dolog = log.append

    ctool = getToolByName(self, 'portal_catalog')
    indexes = ctool.indexes()
    if 'cps_filter_sets' in indexes:
        index = ctool._catalog.getIndex('cps_filter_sets')
        if not index.filteredSets.has_key('nodes'):
            if check:
                return True
            dolog('Reset cps_filter_sets')
            ctool.delIndex('cps_filter_sets')
            # Will then be readded by installer

    if check:
        return False
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

##########

from Products.CPSCore.CPSRegistrationTool import CPSRegistrationTool

def _upgrade_portal_props(portal):
    """Upgrade portal properties."""
    # Get old properties list
    old_prop_ids = portal.propertyIds()

    # Reset _properties to class default
    try:
        delattr(portal, '_properties')
    except AttributeError:
        pass

    # Kill instance variables that may linger from old properties
    # and would thus prevent them from being readded as instance properties
    new_prop_ids = portal.propertyIds()
    for key in set(old_prop_ids)-set(new_prop_ids):
        if key in portal.__dict__:
            delattr(portal, key)

def upgrade_338_340_portal_props(portal):
    """Upgrade portal properties."""
    log = []
    dolog = log.append

    dolog('CPSDefault: Upgrading portal properties.')

    # Move some properties from the portal to portal_membership
    mtool = getToolByName(portal, 'portal_membership')
    for key in ('enable_password_reset',
                'enable_password_reminder'):
        value = portal.__dict__.get(key)
        if value is not None:
            setattr(mtool, key, value)

    # Make sure portal_registration is ours
    rtool = getToolByName(portal, 'portal_registration')
    if rtool.meta_type != CPSRegistrationTool.meta_type:
        portal._delObject('portal_registration')
        portal._setObject('portal_registration', CPSRegistrationTool())
        rtool = getToolByName(portal, 'portal_registration')

    # Move some properties from the portal to portal_registration
    for key in ('enable_portal_joining',
                'validate_email'):
        value = portal.__dict__.get(key)
        if value is not None:
            setattr(rtool, key, value)

    _upgrade_portal_props(portal)

    # Initialize available_languages from Localizer if not present
    if 'available_languages' not in portal.__dict__:
        available_languages = portal.Localizer.get_supported_languages()
        portal.available_languages = tuple(available_languages)

    # Fixup default charset if empty (use class default)
    if 'default_charset' in portal.__dict__ and not portal.default_charset:
        delattr(portal, 'default_charset')

    dolog('CPSDefault: Upgrading portal properties finished.')
    return '\n'.join(log)

def check_338_340_portal_props(portal):
    if 'available_languages' not in portal.__dict__:
        return True
    rtool = getToolByName(portal, 'portal_registration')
    if rtool.meta_type != CPSRegistrationTool.meta_type:
        return True
    if '_properties' not in portal.__dict__:
        return False
    prop_ids = portal.propertyIds()
    class_prop_ids = [p['id'] for p in portal.__class__._properties]
    if len(set(class_prop_ids)-set(prop_ids)):
        # some class prop ids aren't in the instance
        return True
    return False

##########


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
    dolog(upgrade_338_340_portal_props(self))
    return '\n'.join(log)

################################################## Zope 2.8



def upgrade_catalog_Z28(self, check=False):
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

            if found and getattr(idx, '_length', None) is None:
                if check:
                    return True
                dolog('ugrade zope 2.7 catalog index')
                idx._length = idx.__len__
                delattr(idx, '__len__')

    if check:
        return False
    return '\n'.join(log)

def check_upgrade_catalog_Z28(portal):
    """Check if upgrade is needed.
    """
    return upgrade_catalog_Z28(portal, check=True)


def check_migrate_338_340_users(portal):
    return portal.acl_users.meta_type == 'User Folder With Groups'

def migrate_338_340_users(portal):
    """Migrate users/roles/groups"""
    from Products.CPSUserFolder.CPSUserFolder import CPSUserFolder
    from Products.CPSDirectory.ZODBDirectory import ZODBDirectory
    from Products.CPSDirectory.interfaces import IContentishDirectory

    roles = []
    groups = []
    members= []

    mtool = portal.portal_membership
    members_dir = portal.portal_directories.members
    roles_dir = portal.portal_directories.roles
    groups_dir = portal.portal_directories.groups

    # Dump user/roles/groups
    for member in mtool.listMembers():
        entry = {
            'id': member.getMemberId(),
            'password': member.getPassword(),
            'roles': [role for role in member.getRoles()
                      if role != 'Authenticated'],
            'domains': member.getDomains(),
            'sn': member.sn,
            'fullname': member.fullname,
            'givenName': member.givenName,
            'email': member.email,
            'groups': member.getGroups(),
            'homeless': member.homeless,
            }
        members.append(entry)

    return_fields = ['group', 'members', 'subgroup']
    for gid, entry in groups_dir.searchEntries(return_fields=return_fields):
        entry['id'] = gid
        groups.append(entry)

    return_fields = ['role', 'members']
    for rid, entry in roles_dir.searchEntries(return_fields=return_fields):
        entry['id'] = rid
        roles.append(entry)

    # Remove directories and acl_users
    portal.manage_delObjects(['acl_users'])

    dmeta_types = ['CPS Groups Directory', 'CPS Roles Directory',
                   'CPS Members Directory']
    dirs = portal.portal_directories
    for dir_id in dirs.objectIds():
        dobj = dirs._getOb(dir_id)
        if dobj.meta_type in dmeta_types:
            dirs._delObject(dir_id)

    # Create directories
    dir_ids = dirs.objectIds()
    for dir_id in 'groups', 'roles', 'members':
        if dir_id not in dir_ids:
            dirs._setObject(dir_id, ZODBDirectory(dir_id))

    roles_dir = dirs._getOb('roles')
    if IContentishDirectory.providedBy(roles_dir):
        data = {
            'title': 'label_roles',
            'schema': 'roles',
            'layout': 'roles',
            'layout_search': 'roles_search',
            'role_field': 'role',
            'members_field': 'members',
            'title_field': 'role',
            'search_substring_fields': ['role'],
            'acl_directory_view_roles': 'Manager',
            'acl_entry_view_roles': 'Manager',
            }
        roles_dir.manage_changeProperties(**data)
        for entry in roles:
            roles_dir.createEntry(entry)

    members_dir = dirs._getOb('members')
    if IContentishDirectory.providedBy(members_dir):
        data = {
            'title': 'label_members',
            'schema': 'members',
            'layout': 'members',
            'schema_search': 'members_search',
            'layout_search': 'members_search',
            'id_field': 'id',
            'password_field': 'password',
            'roles_field': 'roles',
            'groups_field': 'groups',
            'title_field': 'fullname',
            'search_substring_fields': ['id', 'sn', 'givenName', 'email'],
            'acl_directory_view_roles': 'Manager; Member',
            }
        members_dir.manage_changeProperties(**data)

    groups_dir = dirs._getOb('groups')
    if IContentishDirectory.providedBy(groups_dir):
        data = {
            'title': 'label_groups',
            'schema': 'groups',
            'layout': 'groups',
            'layout_search': 'groups_search',
            'group_field': 'group',
            'members_field': 'members',
            'title_field': 'group',
            'search_substring_fields': ['group'],
            'acl_directory_view_roles': 'Manager; Member',
            }
        groups_dir.manage_changeProperties(**data)
        for entry in groups:
            groups_dir.createEntry(entry)

    # Recreating users
    portal._setObject('acl_users', CPSUserFolder())
    acl_users = portal._getOb('acl_users')
    data = {
        'users_dir': 'members',
        'groups_dir': 'groups',
        'groups_members_field': 'members',
        'roles_dir': 'roles',
        'roles_members_field': 'members',
        'users_groups_field': 'groups',
        'users_login_field': 'id',
        'users_password_field': 'password',
        'users_roles_field': 'roles',
        'cache_timeout': '1',
        }
    acl_users.manage_changeProperties(**data)

    for entry in members:
       name = entry.pop('id')
       password = entry.pop('password')
       roles = entry.pop('roles')
       domains = entry.pop('domains')
       groups = entry.pop('groups')

       acl_users._doAddUser(name, password, roles, domains, groups, **entry)

def check_upgrade_338_340_members_folder(portal):
    ws_ids = portal.workspaces.objectIds()
    portal_ids = portal.objectIds()
    return ('members' in ws_ids) and ('members' in portal_ids)

def upgrade_338_340_members_folder(portal):
    """Move user folders from /workspaces/members to /members"""
    old_members_folder = portal.workspaces.members
    new_members_folder = portal.members
    folder_ids = [oid for oid in old_members_folder.objectIds()
                  if not oid.startswith('.')]

    info = old_members_folder.manage_cutObjects(folder_ids)
    new_members_folder.manage_pasteObjects(info)

    # Remove old members folder
    portal.workspaces.manage_delObjects('members')

##########

def upgrade_338_340_old_skin_layers(portal, check=False):
    """Remove broken skin layers.
    """
    from Products.CMFCore.DirectoryView import _dirreg
    from Products.CMFCore.DirectoryView import DirectoryViewSurrogate
    res = []
    for id, surrogate in portal.portal_skins.objectItems():
        if not isinstance(surrogate, DirectoryViewSurrogate):
            continue
        if surrogate._objects:
            continue
        dv = portal.portal_skins.__dict__[id] # avoid __of__ wrapping
        if _dirreg.getDirectoryInfo(dv._dirpath) is None:
            if check:
                return True
            res.append(id)
    if check:
        return False
    for id in res:
        portal.portal_skins._delObject(id)
    msg = "%d old skin layers removed" % len(res)
    LOG('Upgrade', DEBUG, msg)
    return msg

def check_338_340_old_skin_layers(portal):
    return upgrade_338_340_old_skin_layers(portal, check=True)


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
