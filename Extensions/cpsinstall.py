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
"""Installer for a default CPS site.
"""

from AccessControl import getSecurityManager
from zLOG import LOG, INFO, DEBUG

from Products.CMFCore.permissions import setDefaultRoles
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.CMFCore.Expression import Expression
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION

from Products.CPSWorkflow.transitions import \
     TRANSITION_INITIAL_PUBLISHING, TRANSITION_INITIAL_CREATE, \
     TRANSITION_ALLOWSUB_CREATE, TRANSITION_ALLOWSUB_PUBLISHING, \
     TRANSITION_BEHAVIOR_PUBLISHING, TRANSITION_BEHAVIOR_FREEZE, \
     TRANSITION_BEHAVIOR_DELETE, TRANSITION_BEHAVIOR_MERGE, \
     TRANSITION_ALLOWSUB_CHECKOUT, TRANSITION_INITIAL_CHECKOUT, \
     TRANSITION_BEHAVIOR_CHECKOUT, TRANSITION_ALLOW_CHECKIN, \
     TRANSITION_BEHAVIOR_CHECKIN, TRANSITION_ALLOWSUB_DELETE, \
     TRANSITION_ALLOWSUB_MOVE, TRANSITION_ALLOWSUB_COPY
from Products.CPSInstaller.CPSInstaller import CPSInstaller
from Products.CPSCore.URLTool import URLTool

from Products.CPSDefault.MembershipTool import MembershipTool
from Products.CPSDefault.document import schemas
from Products.CPSDefault.document import layouts
from Products.CPSDefault.document import vocabularies

try:
    import transaction
except ImportError: # BBB: for Zope 2.7
    from Products.CMFCore.utils import transaction

# Zope permissions
AccessContentsInformation = 'Access contents information'
ChangePermissions = 'Change permissions'
DeleteObjects = 'Delete objects'
ViewManagementScreens = 'View management screens'
WebDavLockItem = 'WebDAV Lock items'
WebDavUnlockItem = 'WebDAV Unlock items'

# CMF permissions
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import RequestReview
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.permissions import AddPortalFolders
from Products.CMFCore.permissions import ListFolderContents

# ExternalEditor permissions
try:
    from Products.ExternalEditor.ExternalEditor import ExternalEditorPermission
    external_editor_present = 1
except ImportError:
    external_editor_present = 0

# CPSCore permissions
from Products.CPSCore.permissions import ViewArchivedRevisions
from Products.CPSCore.permissions import ChangeSubobjectsOrder

# CPSDefault permissions
# XXX should be imported from somewhere
ModifyFolderProperties = 'Modify Folder Properties'

SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'
MEMBERS_ID = 'members'


class DefaultInstaller(CPSInstaller):

    product_name = 'CPSDefault'
    DEFAULT_CPS_LEXICON_ID = 'cps_defaut_lexicon'
    DEFAULT_CPS_LEXICON_TITLE = 'CPS Default Lexicon for ZCTextIndex'

    CPS_FILTER_SETS_INDEX = 'cps_filter_sets'
    # this set is supposed to match anything that can be viewed
    # ie anything except document in portal_repository
    CPS_FILTER_SEARCHABLE_SET = 'searchable'
    CPS_FILTER_SEARCHABLE_EXPR = """not filter(lambda s: s.startswith('portal_') or s and s[0] in ('.', '_'), o.getPhysicalPath())"""
    CPS_FILTER_NODES_SET = 'nodes'
    CPS_FILTER_NODES_EXPR = """o.isCPSFolderish()"""
    CPS_FILTER_LEAVES_SET = 'leaves'
    CPS_FILTER_LEAVES_EXPR = """not o.isCPSFolderish()"""
    # this following filter matches all proxies in their default languages,
    # this is usefull to remove all translations of a same proxy
    # match also all non proxy objects and should be used with searchable set
    CPS_FILTER_DEFAULT_LANGUAGES_SET = 'default_languages'
    CPS_FILTER_DEFAULT_LANGUAGES_EXPR = "not hasattr(o, 'isDefaultLanguage') or o.isDefaultLanguage()"


    WFS_MANAGE_PROXY_LANGUAGES = {
        'add_language_to_proxy': {
            '_owner': None,
            'script': """\
##parameters=state_change
lang=state_change.kwargs.get('lang')
from_lang=state_change.kwargs.get('from_lang')
state_change.object.addLanguageToProxy(lang, from_lang)
"""
            },
        'delete_language_from_proxy': {
            '_owner': None,
            'script': """\
##parameters=state_change
lang=state_change.kwargs.get('lang')
state_change.object.delLanguageFromProxy(lang)
"""
            },
        }

    # skins resources cached by default using the CMF Cache Policy Manager
    DEFAULT_CACHED_META_TYPES = ('Filesystem Image',)

    def install(self, langs_list=None, is_creation=0):
        """Main installer
        """
        self.langs_list = langs_list
        self.is_creation = is_creation

        self.log("Starting CPS update")
        self.log("")
        installername = getSecurityManager().getUser().getUserName()
        self.log("Current user: %s" % installername)

        # Automatic upgrades
        self.doUpgrades(post_update=False)

        self.setupRegistration()
        self.setupMembership()
        self.setupTools()
        self.setupSkins()
        self.setupEventService()

        # Disable useless subscribers during installation
        self.disableEventSubscriber('portal_trees')
        self.disableEventSubscriber('portal_subscriptions')

        self.setupTypes()
        self.setupActions()
        self.setupWorkflow()
        # XXX: setup i18n before default roots because default language will
        # then be set (instead of defaulting to 'en')
        self.setupi18n()
        self.setupCatalog()
        self.setupRoots()
        self.setupAccessControl()
        self.setupLocalWorkflow()
        self.upgradeWorkflowStatus()
        self.setupTreesTool()

        # Don't update if no dedicated boxes instance
        self.setupCPSProducts()
        if self.is_creation:
            self.setupPortlets()
        self.setupCustomDocuments()

        self.log("Verifying private area creation flag")
        if not self.portal.portal_membership.getMemberareaCreationFlag():
            self.log(" Activated")
            self.portal.portal_membership.setMemberareaCreationFlag()
        else:
            self.logOK()

        # remove cpsinstall external method
        # and fix cpsupdate permission
        if 'cpsinstall' in self.portal.objectIds():
            self.log("Removing cpsinstall")
            self.portal._delObject('cpsinstall')

        self.setupTranslations()
        # setup roots translated titles after message catalog and translations
        # have been installed
        self.setupRootsi18n()
        # fixupRoots is a temporary hack to fix a CPSDocument bootstrap problem
        self.fixupRoots()
        self.setupCachingPolicyManager()
        self.log("CPS update Finished")
        self.verifyVHM()

        # Re-enable subscribers
        self.enableEventSubscriber('portal_trees')
        self.enableEventSubscriber('portal_subscriptions')

        # Automatic upgrades
        self.doUpgrades(post_update=True)

    #
    # Catalog
    #
    def catalogEnumerateIndexes(self):
        """Return a list of (index_name, type) pairs for the initial
        index set.
        """
        class Struct:
            def __init__(self, **kw):
                for k, v in kw.items():
                    setattr(self, k, v)

        return (('Title', 'FieldIndex', None), # used for sorting
                ('ZCTitle', 'ZCTextIndex',  # used for searching
                 Struct(doc_attr='Title',
                        lexicon_id=self.DEFAULT_CPS_LEXICON_ID,
                        index_type='Okapi BM25 Rank')),
                ('Subject', 'KeywordIndex', None),
                ('Description', 'ZCTextIndex',
                 Struct(doc_attr='Description',
                        lexicon_id=self.DEFAULT_CPS_LEXICON_ID,
                        index_type='Okapi BM25 Rank')),
                ('Creator', 'FieldIndex', None),
                ('SearchableText', 'ZCTextIndex',
                 Struct(doc_attr='SearchableText',
                        lexicon_id=self.DEFAULT_CPS_LEXICON_ID,
                        index_type='Okapi BM25 Rank')),
                ('Date', 'DateIndex', None),
                ('Type', 'FieldIndex', None),
                ('created', 'DateIndex', None),
                ('effective', 'DateIndex', None),
                ('expires', 'DateIndex', None),
                ('modified', 'DateIndex', None),
                ('allowedRolesAndUsers', 'KeywordIndex', None),
                ('localUsersWithRoles', 'KeywordIndex', None),
                ('review_state', 'FieldIndex', None),
                ('in_reply_to', 'FieldIndex', None),
                ('meta_type', 'FieldIndex', None),
                ('id', 'FieldIndex', None),
                ('getId', 'FieldIndex', None),
                ('path', 'PathIndex', None),
                ('portal_type', 'FieldIndex', None),
                (self.CPS_FILTER_SETS_INDEX, 'TopicIndex',
                 (Struct(id=self.CPS_FILTER_SEARCHABLE_SET,
                         expr=self.CPS_FILTER_SEARCHABLE_EXPR),
                  Struct(id=self.CPS_FILTER_LEAVES_SET,
                         expr=self.CPS_FILTER_LEAVES_EXPR),
                  Struct(id=self.CPS_FILTER_NODES_SET,
                         expr=self.CPS_FILTER_NODES_EXPR),
                  Struct(id=self.CPS_FILTER_DEFAULT_LANGUAGES_SET,
                         expr=self.CPS_FILTER_DEFAULT_LANGUAGES_EXPR),)),
                ('start', 'DateIndex', None),
                ('end', 'DateIndex', None),
                ('time', 'DateIndex', None), # time of the last transition
                ('Language', 'FieldIndex', None),
                ('container_path', 'FieldIndex', None),
                ('position_in_container', 'FieldIndex', None),
                )

    def catalogEnumerateMetadata(self):
        """Return a sequence of schema names to be cached (catalog metadata).
        """
        # id is deprecated and may go away, use getId!
        return (# CMF metadata
                'Subject',
                'Title',
                'Description',
                'Type',
                'review_state',
                'Creator',
                'Date',
                'getIcon',
                'created',
                'effective',
                'expires',
                'modified',
                'CreationDate',
                'EffectiveDate',
                'ExpirationDate',
                'ModificationDate',
                'id',
                'getId',
                'portal_type',
                # CPS metadata
                'Contributors',
                'Language',
                'start',
                'end',
                'getRevision',
                # Time of the last transition
                'time',
                'position_in_container',
                )

    def setupCatalog(self):
        # check default ZCTextIndex lexicon
        self.addZCTextIndexLexicon(self.DEFAULT_CPS_LEXICON_ID,
                                   self.DEFAULT_CPS_LEXICON_TITLE)
        # check indexes
        for index_name, index_type, index_extra in \
                self.catalogEnumerateIndexes():
            self.addPortalCatalogIndex(index_name, index_type, index_extra)
        # check metadata
        for name in self.catalogEnumerateMetadata():
            self.addPortalCatalogMetadata(name)

    def setupAccessControl(self):
        # setting roles
        # acl_users with group
        self.log("Verifying User Folder")
        if self.portalHas('acl_users'):
            aclu = self.portal.acl_users
            # Change from earlier installer; Now only replaces the user folder
            # if it is an empty standard user folder. If it is NOT, somebody
            # has already replaced it, and it should be kept.
            if aclu.meta_type == 'User Folder':
                if aclu.getUserNames():
                    self.log('WARNING: You are not using a CPS compatible '
                        'user folder! The current user folder will not be '
                        'replaced this userfolder as it contains users. '
                        'Please upgrade manually.')
                else:
                    self.log(' Replacing default user folder')
                    self.portal.manage_delObjects(['acl_users'])
        if not self.portalHas('acl_users'):
            self.log(" Creating User Folder With Groups")
            self.portal.manage_addProduct['CPSUserFolder'].\
                addUserFolderWithGroups()

        self.verifyRoles((
            # A role that can modify documents and can ask for publication.
            # This role is not specific to workspaces or sections.
            # This role is what WorkspaceMember should have been in the first
            # place.
            # This role is used at least in CPSWiki.
            'Contributor',
            # A role that can view documents.
            # This role is not specific to workspaces or sections.
            # This role is what WorkspaceReader and SectionReader should have
            # been in the first place.
            # This role is used at least in CPSWiki.
            'Reader',
            # A role that can manage objects and sub-objects, user rights,
            # documents and can ask for publication.
            'WorkspaceManager',
            # A role that can manage documents and can ask for publication
            'WorkspaceMember',
            # A role that can only view documents
            'WorkspaceReader',
            # A role that can manage objects and sub-objects, user rights,
            # documents, and accept/accept publications.
            'SectionManager',
            # A role that can accept/reject publications.
            'SectionReviewer',
            # A role that can only view published documents.
            'SectionReader',
        ))

        self.log("Verifying permissions")
        setDefaultRoles(ModifyFolderProperties,
            ('Manager', 'WorkspaceManager',))

        if external_editor_present:
            portal_perms = {
                ExternalEditorPermission: ['Manager', 'Member'],
                }
            self.setupPortalPermissions(portal_perms, self.portal)
        sections_perms = {
            RequestReview: ['Manager', 'WorkspaceManager',
                               'WorkspaceMember', 'Contributor',
                               'SectionReviewer', 'SectionManager'],
            ReviewPortalContent: ['Manager', 'SectionReviewer',
                                      'SectionManager'],
            AddPortalContent: ['Manager', 'SectionManager', 'Contributor'],
            AddPortalFolders: ['Manager', 'SectionManager'],
            ChangePermissions: ['Manager', 'SectionManager'],
            ChangeSubobjectsOrder: ['Manager', 'SectionManager',
                                    'SectionReviewer'],
            DeleteObjects: ['Manager', 'SectionManager', 'SectionReviewer'],
            ListFolderContents: ['Manager', 'SectionManager',
                                     'SectionReviewer', 'SectionReader',
                                     'Contributor'],
            ModifyPortalContent: ['Manager', 'SectionManager',
                                      'Contributor'],
            ModifyFolderProperties: ['Manager', 'SectionManager'],
            View: ['Manager', 'SectionManager', 'SectionReviewer',
                     'SectionReader', 'Contributor'],
            ViewManagementScreens: ['Manager', 'SectionManager'],
            ViewArchivedRevisions: ['Manager', 'SectionManager',
                                        'SectionReviewer', 'Contributor'],
            WebDavLockItem: ['SectionManager', 'SectionReviewer'],
            WebDavUnlockItem: ['SectionManager', 'SectionReviewer'],
            }
        self.setupPortalPermissions(sections_perms, self.portal[SECTIONS_ID])
        workspaces_perms = {
            AddPortalContent: ['Manager', 'WorkspaceManager',
                                   'WorkspaceMember', 'Contributor'],
            AddPortalFolders: ['Manager', 'WorkspaceManager'],
            ChangePermissions: ['Manager', 'WorkspaceManager'],
            ChangeSubobjectsOrder: ['Manager', 'WorkspaceManager',
                                        'WorkspaceMember', 'Contributor'],
            DeleteObjects: ['Manager', 'WorkspaceManager',
                               'WorkspaceMember', 'Contributor'],
            ListFolderContents: ['Manager', 'WorkspaceManager',
                                     'WorkspaceMember', 'Contributor', 'WorkspaceReader'],
            ModifyPortalContent: ['Manager', 'WorkspaceManager',
                                      'WorkspaceMember', 'Contributor', 'Owner'],
            ModifyFolderProperties: ['Manager', 'WorkspaceManager'],
            View: ['Manager', 'WorkspaceManager', 'WorkspaceMember', 'Contributor',
                     'WorkspaceReader'],
            ViewManagementScreens: ['Manager', 'WorkspaceManager',
                                        'WorkspaceMember', 'Contributor'],
            ViewArchivedRevisions: ['Manager', 'WorkspaceManager',
                                        'WorkspaceMember', 'Contributor'],
            WebDavLockItem: ['WorkspaceManager', 'WorkspaceMember', 'Contributor', 'Owner'],
            WebDavUnlockItem: ['WorkspaceManager', 'WorkspaceMember', 'Owner'],
            }
        self.setupPortalPermissions(workspaces_perms, self.portal[WORKSPACES_ID])

        # Protect repository, no access allowed
        repo_perms = {
            AccessContentsInformation: ['Manager'],
            ListFolderContents: ['Manager'],
            ModifyPortalContent: ['Manager'],
            View: ['Manager'],
            }
        self.setupPortalPermissions(repo_perms,
                                    self.portal.portal_repository)

        if 'cpsupdate' in self.portal.objectIds():
            self.log("Protecting cpsupdate")
            self.portal.cpsupdate.manage_permission(
                View, roles=['Manager'], acquire=0)
            self.portal.cpsupdate.manage_permission(
                AccessContentsInformation, roles=['Manager'], acquire=0)

    def setupRegistration(self):
        self.log("Setting up portal registration tool")
        self.verifyTool('portal_registration', 'CPSCore',
                        'CPS Registration Tool')

    def setupMembership(self):
        self.log('Setting up portal membership support,')
        portal = self.portal

        # Previous versions of CPS were installing a MembershipTool from CPSCore
        # while newer versions install the MembershipTool from CPSDefault which
        # provides additional services.
        self.verifyTool('portal_membership', 'CPSDefault',
                        MembershipTool.meta_type, type(MembershipTool))

        # Adding properties that previous versions of CPS portal didn't have.
        # All this code is complicated because in the past some values were not
        # stored in a good manner (as properties) in the portal.
        # XXX the joining preferences should be on the membership tool
        properties = [['enable_password_reset', True, 'boolean'],
                      ['enable_password_reminder', False, 'boolean'],
                      ['enable_portal_joining', False, 'boolean'],
                      ]
        for prop in properties:
            if not portal.hasProperty(prop[0]):
                if portal.__dict__.has_key(prop[0]):
                    # This code converts possible old bad way to store those
                    # variables.
                    # This value was set as an instance variable.
                    value = getattr(portal, prop[0])
                    delattr(portal, prop[0])
                    # Adding this property back as a property from the
                    # PropertyManager.
                    portal.manage_addProperty(prop[0], value, prop[2])
                else:
                    # Adding the new properties that are declared as class
                    # variables but that might not be already present in the
                    # properties of the portal.
                    portal._properties += tuple([p for p in portal.__class__._properties
                                                 if p['id'] == prop[0]])

        for action in portal['portal_registration'].listActions():
            if action.id == 'join':
                action.condition = Expression('python: portal.'
                    'portal_properties.enable_portal_joining and not member')
                break

        self.verifyAction('portal_membership',
                id='preferences',
                name='action_my_preferences',
                action="string:${portal_url}/cpsdirectory_entry_view?"
                       "dirname=members&id=${member}",
                condition='python:member and member.has_role("Member")',
                permission=(View,),
                category='user',
                visible=1)

    def setupActions(self):

        if self.is_creation:
            self.log("Cleaning actions")
            actiondelmap = {
                'portal_actions': ('folderContents', 'folder_contents'),
                'portal_syndication': ('syndication',),
            }
            self.deleteActions(actiondelmap)

        # Setting up misc actions
        actions = (
          { 'tool': 'portal_actions',
            'id': 'accessibility',
            'name': 'action_accessibility',
            'action': 'string:${portal_url}/accessibility',
            'permission': (View, ),
            'condition': '',
            'category': 'global_header',
            'visible': 1,
          },
          { 'tool': 'portal_actions',
            'id': 'print',
            'name': 'action_print',
            'action':
            'string:javascript:if%20(window.print)%20window.print();',
            'permission': (View,),
            'condition': '',
            'category': 'global_header',
            'visible': 1
          },
          { 'tool': 'portal_actions',
            'id': 'advanced_search',
            'name': 'action_advanced_search',
            'action': 'string:./advanced_search_form',
            'permission': (View, ),
            'condition': '',
            'category': 'global_header',
            'visible': 1,
          },
          { 'tool': 'portal_actions',
            'id': 'contact',
            'name': 'action_contact',
            'action': 'string:mailto:${portal/portal_properties/'
                      'email_from_address}?subject=Info',
            'permission': (View, ),
            'condition': '',
            'category': 'global_header',
            'visible': 1,
          },
          { 'tool': 'portal_actions',
            'id': 'manage_vocabularies',
            'name': 'action_manage_vocabularies',
            'action': 'string:${portal_url}/vocabularies_manage_form',
            'permission': (ModifyPortalContent, ),
            'condition': '',
            'category': 'global',
            'visible': 1,
          },
          { 'tool': 'portal_actions',
            'id': 'manage_languages',
            'name': 'action_manage_languages',
            'action': 'string:${portal_url}/language_manage_form',
            'permission': (ModifyPortalContent, ),
            'condition': '',
            'category': 'global',
            'visible': 1,
          },
        )

        if 'Link' in self.portal['portal_types'].objectIds():
            actions = actions + (
                { 'tool': 'portal_actions',
                    'id': 'add_favorites',
                    'name': 'action_add_favorites',
                    'action': 'string:${object/absolute_url}/addtoFavorites',
                    'permission': (View, ),
                    'condition': "python: member and portal.portal_membership."
                                 "getHomeFolder()",
                    'category': 'user',
                    'visible': 1,
                },
                { 'tool': 'portal_actions',
                    'id': 'view_favorites',
                    'name': 'action_view_favorites',
                    'action': 'string:${portal/portal_membership/getHomeUrl}/'
                              'Favorites',
                    'permission': (View, ),
                    'condition': 'python: hasattr(portal.portal_membership.'
                                 'getHomeFolder(),"Favorites")',
                    'category': 'user',
                    'visible': 1,
                },
            )
        else:
            self.log("WARNING: CPSDocument type Link does not seem to exist; "
                     "Favorites will not be available")

        self.verifyActions(actions)

        # Clean old CPS actions.
        if self.hasAction('portal_actions', 'status_history'):
            self.deleteActions({'portal_actions': ('status_history',)})
            self.log("Deleted old 'status_history' action from portal_actions")
        # This one was changed back to the standard CMF 'preferences' id
        if self.hasAction('portal_actions', 'action_my_preferences'):
            self.deleteActions({'portal_actions': ('action_my_preferences',)})


    def setupSkins(self):
        self.deleteSkins(('calendar', 'zpt_calendar'))
        skins = {
            'cps_nuxeo_style': 'Products/CPSDefault/skins/cps_styles/nuxeo',
            'cps_styles': 'Products/CPSDefault/skins/cps_styles',
            'cps_images': 'Products/CPSDefault/skins/cps_images',
            'cps_devel': 'Products/CPSDefault/skins/cps_devel',
            'cps_default': 'Products/CPSDefault/skins/cps_default',
            'cps_javascript': 'Products/CPSDefault/skins/cps_javascript',
            'cmf_zpt_calendar': 'Products/CMFCalendar/skins/zpt_calendar',
            'cmf_calendar': 'Products/CMFCalendar/skins/calendar',
        }
        self.verifySkins(skins)

    def setupTools(self):
        # Needs to exist before types are installed.
        if not self.portalHas("portal_calendar"):
            self.runExternalUpdater('cmfcalendar_installer',
                                    'CMFCalendar Updater',
                                    'CMFCalendar',
                                    'Install',
                                    'install')

        # add tools (CPS Tools): CPS Event Service Tool, CPS Proxies Tool,
        # CPS Object Repository, Tree tools
        self.verifyTool('portal_proxies', 'CPSCore', 'CPS Proxies Tool')
        self.verifyTool('portal_repository', 'CPSCore', 'CPS Repository Tool')

        # replace CMF URLTool by specific CPS one
        self.verifyTool('portal_url', 'CPSCore',
                        URLTool.meta_type, type(URLTool))

    def setupEventService(self):
        # configure event service to hook the proxies, by adding a subscriber
        self.verifyTool('portal_eventservice', 'CPSCore',
                        'CPS Event Service Tool')
        subscriptions = (
            {
                'subscriber': 'portal_proxies',
                'action': 'proxy',
                'meta_type': '*',
                'event_type': '*',
                'notification_type': 'synchronous',
            },
            {
                'subscriber': 'portal_trees',
                'action': 'tree',
                'meta_type': '*',
                'event_type': '*',
                'notification_type': 'synchronous'
             }
        )
        self.verifyEventSubscribers(subscriptions)

    def setupWorkflow(self):
        # replace portal_workflow with a (CPS Tools) CPS Workflow Tool.
        self.verifyTool('portal_workflow', 'CPSWorkflow', 'CPS Workflow Tool')
        self.setupWorkflow1()
        self.setupWorkflow2()
        self.setupWorkflow3()
        self.setupWorkflow4()
        self.setupWorkflow5()
        self.addModifyTransition()
        self.setupWorkflowTranslation()
        self.log("Verifying workflow schemas")

        wfs = {
            'Section': 'section_folder_wf',
            'Workspace': 'workspace_folder_wf',
            }
        wftool = self.portal.portal_workflow
        self.log("Installing workflow schemas")
        for pt, chain in wfs.items():
            wftool.setChainForPortalTypes([pt], chain)
        wftool.setDefaultChain('')

    def setupLocalWorkflow(self):
        wfchains = {'Workspace': 'workspace_folder_wf',
                    'Section': ''}
        self.verifyLocalWorkflowChains(self.portal[WORKSPACES_ID], wfchains)

        wfchains = {'Workspace': '',
                    'Section': 'section_folder_wf'}
        self.verifyLocalWorkflowChains(self.portal[SECTIONS_ID], wfchains)


    def setupWorkflow1(self):
        # workspace_folder_wf
        wfdef = {'wfid': 'workspace_folder_wf',
                 'permissions': (View,),
                 'state_var': 'review_state',
                 }

        wfstates = {
            'work': {
                'title': 'Work',
                'transitions': ('create_content', 'cut_copy_paste', 'modify'),
                'permissions': {View: ('Manager', 'WorkspaceManager',
                                       'WorkspaceMember', 'WorkspaceReader')},
            },
        }

        wftransitions = {
            'cut_copy_paste': {
                'title': 'Cut/Copy/Paste',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_ALLOWSUB_DELETE,
                                        TRANSITION_ALLOWSUB_MOVE,
                                        TRANSITION_ALLOWSUB_COPY),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': '',
                'actbox_category': '',
                'actbox_url': '',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
            'create': {
                'title': 'Initial creation',
                'new_state_id': 'work',
                'transition_behavior': (TRANSITION_INITIAL_CREATE,),
                'clone_allowed_transitions': None,
                'actbox_category': 'workflow',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                        'WorkspaceMember',
                          'guard_expr': ''},
            },
            'create_content': {
                'title': 'Create content',
                'new_state_id': 'work',
                'transition_behavior': (TRANSITION_ALLOWSUB_CREATE,
                                        TRANSITION_ALLOWSUB_CHECKOUT),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': '',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
            'modify': {
                'title': 'Edit content',
                'description': 'This transition provides a specific entry in status history',
                'new_state_id': '',
                'transition_behavior': (),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_category': 'workflow',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; Owner;'
                                         'WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
        }
        self.verifyWorkflow(wfdef, wfstates, wftransitions,
                            self.WFS_MANAGE_PROXY_LANGUAGES, {})


    def setupWorkflow2(self):
        # workspace_content_wf
        wfdef = {'wfid': 'workspace_content_wf',
                 'permissions': (View, ModifyPortalContent,
                                 WebDavLockItem, WebDavUnlockItem,),
                 'state_var': 'review_state',
                 }

        wfstates = {
            'work': {
                'title': 'Work',
                'transitions': ('copy_submit', 'checkout_draft',
                                'cut_copy_paste', 'modify'),
                'permissions': {View: ('Manager', 'WorkspaceManager',
                                        'WorkspaceMember', 'WorkspaceReader'),
                                ModifyPortalContent: ('Manager', 'Owner',
                                   'WorkspaceManager', 'WorkspaceMember'),
                                WebDavLockItem: ('Manager', 'Owner',
                                   'WorkspaceManager', 'WorkspaceMember'),
                                WebDavUnlockItem: ('Manager', 'Owner',
                                   'WorkspaceManager', 'WorkspaceMember')},
           },
            'draft': {
                'title': 'Draft',
                'transitions': ('checkin_draft', 'abandon_draft', 'unlock'),
                'permissions': {View: ('Manager', 'WorkspaceManager',
                                       'WorkspaceMember', 'Owner'),
                                ModifyPortalContent:
                                    ('Manager', 'WorkspaceManager', 'Owner'),
                                WebDavLockItem:
                                    ('Manager', 'WorkspaceManager', 'Owner'),
                                WebDavUnlockItem:
                                    ('Manager', 'WorkspaceManager', 'Owner')},
            },
            'locked': {
                'title': 'Locked',
                'transitions': ('unlock',),
                'permissions': {View: ('Manager', 'WorkspaceManager',
                                         'WorkspaceMember', 'WorkspaceReader'),
                                ModifyPortalContent: (),
                                WebDavLockItem: (),
                                WebDavUnlockItem: ()},
            },
        }

        wftransitions = {
            'create': {
                'title': 'Initial creation',
                'new_state_id': 'work',
                'transition_behavior': (TRANSITION_INITIAL_CREATE, ),
                'clone_allowed_transitions': None,
                'actbox_name': '',
                'actbox_category': 'workflow',
                'actbox_url': '',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
            'copy_submit': {
                'title': 'Copy content into a section for Publishing',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_BEHAVIOR_PUBLISHING, ),
                'clone_allowed_transitions': ('submit', 'publish'),
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': 'action_submit',
                'actbox_category': 'workflow',
                'actbox_url': '%(content_url)s/content_submit_form',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
            'checkout_draft': {
                'title': 'Checkout content into a draft',
                'new_state_id': 'locked',
                'transition_behavior': (TRANSITION_BEHAVIOR_CHECKOUT,),
                'checkout_allowed_initial_transitions': ('checkout_draft_in',),
                'actbox_name': 'action_checkout_draft',
                'actbox_category': 'workflow',
                'actbox_url': '%(content_url)s/content_checkout_draft_form',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
            'checkout_draft_in': {
                'title': 'Draft is created',
                'new_state_id': 'draft',
                'transition_behavior': (TRANSITION_INITIAL_CHECKOUT,
                                        TRANSITION_BEHAVIOR_FREEZE),
            },
            'checkin_draft': {
                'title': 'Checkin draft',
                'new_state_id': 'locked',
                'transition_behavior': (TRANSITION_BEHAVIOR_CHECKIN,),
                'checkin_allowed_transitions': ('unlock',),
                'actbox_name': 'action_checkin_draft',
                'actbox_category': 'workflow',
                'actbox_url': '%(content_url)s/content_checkin_draft_form',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'Owner',
                          'guard_expr': ''},
            },
            'abandon_draft': {
                'title': 'Abandon draft',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_BEHAVIOR_DELETE,),
                'script_name': 'unlock_locked_before_abandon',
                'actbox_name': 'action_abandon_draft',
                'actbox_category': 'workflow',
                'actbox_url': '%(content_url)s/content_abandon_draft_form',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'Owner',
                          'guard_expr': ''},
            },
            'unlock': {
                'title': 'Unlock content after a draft is done',
                'new_state_id': 'work',
                'transition_behavior': (TRANSITION_ALLOW_CHECKIN,),
            },
            'cut_copy_paste': {
                'title': 'Cut/Copy/Paste',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_ALLOWSUB_DELETE,
                                        TRANSITION_ALLOWSUB_MOVE,
                                        TRANSITION_ALLOWSUB_COPY),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': '',
                'actbox_category': '',
                'actbox_url': '',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
            'modify': {
                'title': 'Edit content',
                'description': 'This transition provides a specific entry in status history',
                'new_state_id': '',
                'transition_behavior': (),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_category': 'workflow',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; Owner;'
                                         'WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
        }


        wfscripts = {
            'unlock_locked_before_abandon': {
                '_owner': None,
                'script': """\
##parameters=state_change
return state_change.object.content_unlock_locked_before_abandon(state_change)
"""
            },}
        wfscripts.update(self.WFS_MANAGE_PROXY_LANGUAGES)

        wfvariables = {
            'action': {
                'description': 'The last transition',
                'default_expr': 'transition/getId|nothing',
                'for_status': 1,
                'update_always': 1,
            },
            'actor': {
                'description': 'The ID of the user who performed',
                'default_expr': 'user/getId',
                'for_status': 1,
                'update_always': 1,
            },
            'comments': {
                'description': 'Comments about the last transition',
                'default_expr': "python:state_change.kwargs.get('comment', '')",
                'for_status': 1,
                'update_always': 1,
            },
            'review_history': {
                'description': 'Provides access to workflow history',
                'default_expr': 'state_change/getHistory',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember; WorkspaceReader',
                          'guard_expr': ''}
            },
            'language_revs': {
                'description': 'The language revisions of the proxy',
                'default_expr': 'state_change/getLanguageRevisions',
                'for_status': 1,
                'update_always': 1,
            },
            'time': {
                'description': 'Time of the last transition',
                'default_expr': 'state_change/getDateTime',
                'for_status': 1,
                'update_always': 1,
                'for_catalog': 1,
            },
            'dest_container': {
                'description': 'Destination container for the last '
                               'paste/publish',
                'default_expr': "python:state_change.kwargs.get("
                                "'dest_container', '')",
                'for_status': 1,
                'update_always': 1,
            },
        }

        self.verifyWorkflow(wfdef, wfstates, wftransitions,
                            wfscripts, wfvariables)

    def setupWorkflow3(self):
        # WF workspace folderish content
        wfdef = {'wfid': 'workspace_folderish_content_wf',
                 'permissions': (View, ModifyPortalContent,
                                 WebDavLockItem, WebDavUnlockItem,),
                 'state_var': 'review_state',
                 }

        wfstates = {
            'work': {
                'title': 'Work',
                'transitions': ('copy_submit', 'create_content',
                                'cut_copy_paste', 'modify'),
                'permissions': {View: ('Manager', 'WorkspaceManager',
                                       'WorkspaceMember', 'WorkspaceReader'),
                                ModifyPortalContent: ('Manager',
                                       'WorkspaceManager', 'WorkspaceMember'),
                                WebDavLockItem: ('Manager',
                                       'WorkspaceManager', 'WorkspaceMember'),
                                WebDavUnlockItem: ('Manager',
                                       'WorkspaceManager', 'WorkspaceMember')},
           },
        }

        wftransitions = {
           'create': {
                'title': 'Initial creation',
                'new_state_id': 'work',
                'transition_behavior': (TRANSITION_INITIAL_CREATE, ),
                'clone_allowed_transitions': None,
                'actbox_name': '',
                'actbox_category': 'workflow',
                'actbox_url': '',
                'props': {'guard_permissions': '',
                        'guard_roles': 'Manager; WorkspaceManager; '
                                      'WorkspaceMember',
                        'guard_expr': ''},
            },
            'copy_submit': {
                'title': 'Copy content into a section for Publishing',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_BEHAVIOR_PUBLISHING, ),
                'clone_allowed_transitions': ('submit', 'publish'),
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': 'action_submit',
                'actbox_category': 'workflow',
                'actbox_url': '%(content_url)s/content_submit_form',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
            'create_content': {
                'title': 'Create content',
                'new_state_id': 'work',
                'transition_behavior': (TRANSITION_ALLOWSUB_CREATE,
                                        TRANSITION_ALLOWSUB_CHECKOUT,
                                        ),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': '',
                'actbox_category': '',
                'actbox_url': '',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
            'cut_copy_paste': {
                'title': 'Cut/Copy/Paste',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_ALLOWSUB_DELETE,
                                        TRANSITION_ALLOWSUB_MOVE,
                                        TRANSITION_ALLOWSUB_COPY),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': '',
                'actbox_category': '',
                'actbox_url': '',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
            'modify': {
                'title': 'Edit content',
                'description': 'This transition provides a specific entry in status history',
                'new_state_id': '',
                'transition_behavior': (),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_category': 'workflow',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; Owner;'
                                         'WorkspaceManager; '
                                         'WorkspaceMember',
                          'guard_expr': ''},
            },
        }

        wfvariables = {
            'action': {
                'description': 'The last transition',
                'default_expr': 'transition/getId|nothing',
                'for_status': 1,
                'update_always': 1,
            },
            'actor': {
                'description': 'The ID of the user who performed',
                'default_expr': 'user/getId',
                'for_status': 1,
                'update_always': 1,
            },
            'comments': {
                'description': 'Comments about the last transition',
                'default_expr': "python:state_change.kwargs.get('comment', '')",
                'for_status': 1,
                'update_always': 1,
            },
            'review_history': {
                'description': 'Provides access to workflow history',
                'default_expr': 'state_change/getHistory',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; WorkspaceManager; '
                                         'WorkspaceMember; WorkspaceReader',
                          'guard_expr': ''}
            },
            'language_revs': {
                'description': 'The language revisions of the proxy',
                'default_expr': 'state_change/getLanguageRevisions',
                'for_status': 1,
                'update_always': 1,
            },
            'time': {
                'description': 'Time of the last transition',
                'default_expr': 'state_change/getDateTime',
                'for_status': 1,
                'update_always': 1,
                'for_catalog': 1,
            },
            'dest_container': {
                'description': 'Destination container for the last '
                                'paste/publish',
                'default_expr': "python:state_change.kwargs.get("
                                "'dest_container', '')",
                'for_status': 1,
                'update_always': 1,
            },
        }

        self.verifyWorkflow(wfdef, wfstates, wftransitions, {}, wfvariables)

    def setupWorkflow4(self):
        # section_folder_wf
        wfdef = {'wfid': 'section_folder_wf',
                 'permissions': (View,),
                 'state_var': 'review_state',
                 }

        wfstates = {
            'work': {
                'title': 'Work',
                'transitions': ('create_content', 'cut_copy_paste'),
                'permissions': {View: ('Manager', 'SectionManager',
                                       'SectionReviewer', 'SectionReader')},
            },
        }

        wftransitions = {
            'cut_copy_paste': {
                'title': 'Cut/Copy/Paste',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_ALLOWSUB_DELETE,
                                        TRANSITION_ALLOWSUB_MOVE,
                                        TRANSITION_ALLOWSUB_COPY),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': '',
                'actbox_category': '',
                'actbox_url': '',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager; '
                                         'SectionReviewer; SectionReader',
                          'guard_expr': ''},
            },
            'create': {
                'title': 'Initial creation',
                'new_state_id': 'work',
                'transition_behavior': (TRANSITION_INITIAL_CREATE,),
                'clone_allowed_transitions': None,
                'actbox_category': 'workflow',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager;',
                          'guard_expr': ''},
            },
            # XXX: TODO warning guard for publishing and creating
            # sub section are the same
            'create_content': {
                'title': 'Create content',
                'new_state_id': 'work',
                'transition_behavior': (TRANSITION_ALLOWSUB_CREATE,
                                        TRANSITION_ALLOWSUB_PUBLISHING),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager; '
                                         'SectionReviewer; SectionReader',
                          'guard_expr': ''},
            },
        }
        self.verifyWorkflow(wfdef, wfstates, wftransitions,
                            self.WFS_MANAGE_PROXY_LANGUAGES, {})

    def setupWorkflow5(self):
        # section_content_wf
        wfdef = {'wfid': 'section_content_wf',
                 'permissions': (View, ModifyPortalContent,
                                 WebDavLockItem, WebDavUnlockItem,),
                 'state_var': 'review_state',
                 }

        wfstates = {
            'pending': {
                'title': 'Waiting for reviewer',
                'transitions': ('accept', 'reject'),
                'permissions': {View: ('SectionReviewer', 'SectionManager',
                                       'Manager', 'Owner'),
                                ModifyPortalContent: ('SectionReviewer',
                                       'SectionManager', 'Manager'),
                                WebDavLockItem: ('SectionReviewer',
                                       'SectionManager', 'Manager'),
                                WebDavUnlockItem: ('SectionReviewer',
                                       'SectionManager', 'Manager')},
            },
            'published': {
                'title': 'Public',
                'transitions': ('unpublish', 'cut_copy_paste',
                                'sub_publishing'),
                'permissions': {View: ('SectionReader', 'SectionReviewer',
                                       'SectionManager', 'Manager'),
                                ModifyPortalContent: ('Manager',),
                                WebDavLockItem: ('Manager',),
                                WebDavUnlockItem: ('Manager',)},
            },
        }

        wftransitions = {
            'publish': {
                'title': 'Member publishes directly',
                'new_state_id': 'published',
                'transition_behavior': (TRANSITION_INITIAL_PUBLISHING,
                                        TRANSITION_BEHAVIOR_FREEZE,
                                        TRANSITION_BEHAVIOR_MERGE),
                'clone_allowed_transitions': None,
                'after_script_name': 'fixup_after_publish',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager; '
                                         'SectionReviewer',
                          'guard_expr': ''},
            },
            'cut_copy_paste': {
                'title': 'Cut/Copy/Paste',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_ALLOWSUB_DELETE,
                                        TRANSITION_ALLOWSUB_MOVE,
                                        TRANSITION_ALLOWSUB_COPY),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': '',
                'actbox_category': '',
                'actbox_url': '',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager; '
                                        'SectionReviewer',
                          'guard_expr': ''},
            },
            'submit': {
                'title': 'Member requests publishing',
                'new_state_id': 'pending',
                'transition_behavior': (TRANSITION_INITIAL_PUBLISHING,
                                        TRANSITION_BEHAVIOR_FREEZE),
                'clone_allowed_transitions': None,
                'after_script_name': '',
                'actbox_name': '',
                'actbox_category': '',
                'actbox_url': '',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; Member',
                          'guard_expr': ''},
            },
            'accept': {
                'title': 'Reviewer accepts publishing',
                'new_state_id': 'published',
                'transition_behavior': (TRANSITION_BEHAVIOR_MERGE,),
                'clone_allowed_transitions': None,
                'after_script_name': 'fixup_after_publish',
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': 'action_accept',
                'actbox_category': 'workflow',
                'actbox_url': '%(content_url)s/content_accept_form',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager; '
                                         'SectionReviewer',
                          'guard_expr': ''},
            },
            'reject': {
                'title': 'Reviewer rejects publishing',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_BEHAVIOR_DELETE,),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': 'action_reject',
                'actbox_category': 'workflow',
                'actbox_url': '%(content_url)s/content_reject_form',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager; '
                                         'SectionReviewer',
                          'guard_expr': ''},
            },
            'unpublish': {
                'title': 'Reviewer removes content from publication',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_BEHAVIOR_DELETE,),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_name': 'action_un_publish',
                'actbox_category': 'workflow',
                'actbox_url': '%(content_url)s/content_unpublish_form',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager; '
                                         'SectionReviewer',
                          'guard_expr': ''},
            },
            'sub_publishing': {
                'title': 'Allow publishing of subdocuments',
                'new_state_id': '',
                'transition_behavior': (TRANSITION_ALLOWSUB_PUBLISHING,),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager; '
                                         'SectionReviewer; SectionReader',
                          'guard_expr': ''},
            },
        }

        wfscripts = {
            'fixup_after_publish': {
                '_owner': None,
                'script': """\
##parameters=state_change
from Products.CPSWorkflow.util import updateEffectiveDate
return updateEffectiveDate(state_change.object)
"""
            },
        }

        wfvariables = {
            'action': {
                'description': 'The last transition',
                'default_expr': 'transition/getId|nothing',
                'for_status': 1,
                'update_always': 1,
            },
            'actor': {
                'description': 'The ID of the user who performed',
                'default_expr': 'user/getId',
                'for_status': 1,
                'update_always': 1,
            },
            'comments': {
                'description': 'Comments about the last transition',
                'default_expr': "python:state_change.kwargs.get('comment', '')",
                'for_status': 1,
                'update_always': 1,
            },
            'review_history': {
                'description': 'Provides access to workflow history',
                'default_expr': 'state_change/getHistory',
                'props': {'guard_permissions': '',
                          'guard_roles': 'Manager; SectionManager; '
                                         'SectionReviewer',
                          'guard_expr': ''}
            },
            'language_revs': {
                'description': 'The language revisions of the proxy',
                'default_expr': 'state_change/getLanguageRevisions',
                'for_status': 1,
                'update_always': 1,
            },
            'time': {
                'description': 'Time of the last transition',
                'default_expr': 'state_change/getDateTime',
                'for_status': 1,
                'update_always': 1,
                'for_catalog': 1,
            },
            'dest_container': {
                'description': 'Destination container for the last '
                                'paste/publish',
                'default_expr': "python:state_change.kwargs.get("
                                "'dest_container', '')",
                'for_status': 1,
                'update_always': 1,
            },
        }
        self.verifyWorkflow(wfdef, wfstates, wftransitions,
                     wfscripts, wfvariables)


    def addModifyTransition(self):
        wftool = self.getTool('portal_workflow')
        wfs_to_upgrade = ('workspace_content_wf', 'workspace_folder_wf',
                          'workspace_folderish_content_wf')
        modify_transition_def = {
            'modify': {
                'title': 'Edit content',
                'description': 'This transition provides a specific entry in status history',
                'new_state_id': '',
                'transition_behavior': (),
                'clone_allowed_transitions': None,
                'trigger_type': TRIGGER_USER_ACTION,
                'actbox_category': 'workflow',
                'props': {
                    'guard_roles': 'Manager; Owner; WorkspaceManager; WorkspaceMember',
                    },
                }
            }

        for wf_id in wfs_to_upgrade:
            wf = wftool[wf_id]
            self.verifyWfTransitions(wf, modify_transition_def)

            work_state = wf.states.get('work')
            transitions = work_state.transitions
            if 'modify' not in transitions:
                new_transitions = transitions + ('modify',)
                work_state.setProperties(transitions=new_transitions)


    def upgradeWorkflowStatus(self):
        from Products.CPSDefault.Extensions import upgrade
        doit = upgrade.checkUpgradeWorkflows(self.portal)
        if doit:
            self.log("Upgrading old workflow status")
            upgrade.upgradeWorkflows(self.portal)
        else:
            self.log("Workflows status don't need upgrade")


    def setupWorkflowTranslation(self):
        # translate action for folder and workspace content
        wftool = self.portal.portal_workflow
        wf = wftool.section_folder_wf
        for wf in (wftool.section_folder_wf, wftool.workspace_folder_wf,
                   wftool.workspace_content_wf):
            self.log(" Checking wf %s" % wf.getId())
            transitions = wf.transitions

            if hasattr(transitions, 'translate'):
                self.log("  Removing old translate")
                transitions.manage_delObjects('translate')
            transitions.addTransition('translate')
            translate = transitions.get('translate')
            translate.setProperties(
                title="Add translation",
                new_state_id='',
                actbox_name='action_translate',
                actbox_category='workflow',
                actbox_url='%(content_url)s/content_translate_form',
                script_name='add_language_to_proxy',
                props={'guard_permissions': ModifyPortalContent,
                       'guard_roles': '',
                       'guard_expr': ''})
            self.log("  Added translate")
            work_state = wf.states['work']
            transitions = work_state.transitions
            if not 'translate' in transitions:
                # XXX seems nothing is available for just adding a transition
                work_state.transitions = transitions + ('translate',)
                self.log("  translate activated for %s" % wf.getId())

            transitions = wf.transitions
            if hasattr(transitions, 'delete_translation'):
                self.log("  Removing old delete_translation")
                transitions.manage_delObjects('delete_translation')
            transitions.addTransition('delete_translation')
            translate = transitions.get('delete_translation')
            translate.setProperties(
                title="Delete a translation",
                new_state_id='',
                actbox_name='action_delete_translation',
                actbox_category='workflow',
                actbox_url='%(content_url)s/content_delete_translation',
                script_name='delete_language_from_proxy',
                props={'guard_permissions': ModifyPortalContent,
                       'guard_roles': '',
                       'guard_expr': 'python:not state_change.object.isDefaultLanguage()'})
            self.log("  Added delete_translation")
            work_state = wf.states['work']
            transitions = work_state.transitions
            if not 'delete_translation' in transitions:
                # XXX seems nothing is available for just adding a transition
                work_state.transitions = transitions + ('delete_translation',)
                self.log("  delete_translation activated for %s" % wf.getId())


    def setupTypes(self):
        # setup portal_type: CPS Proxy Document, CPS Proxy Folder
        # CPS Folder
        if self.is_creation:
            # Remove some default CPS types:
            ttool = self.getTool('portal_types')
            ttool.manage_delObjects(['Folder',])

        t = 'typeinfo_name'
        amt = 'add_meta_type'
        FTI = 'Factory-based Type Information'
        type_dict = {
            'CPS Proxy Document': {
                t: 'CPSCore: CPS Proxy Document (CPS Proxy Document)',
                amt: FTI,},
            'CPS Proxy Folder': {
                t: 'CPSCore: CPS Proxy Folder (CPS Proxy Folder)',
                amt: FTI,},
            'CPS Proxy Folderish Document': {
                t: 'CPSCore: CPS Proxy Folderish Document (CPS Proxy Folderish Document)',
                amt: FTI,},
            'CPS Proxy BTree Folder': {
                t: 'CPSCore: CPS Proxy BTree Folder (CPS Proxy BTree Folder)',
                amt: FTI,},
            'CPS Proxy BTree Folderish Document': {
                t: 'CPSCore: CPS Proxy BTree Folderish Document (CPS Proxy BTree Folderish Document)',
                amt: FTI,},
            'Section': {
                t: 'CPSDefault: Folder (Folder)',
                amt: FTI,
                'properties': {
                    'title': 'portal_type_Section_title',
                    'description': 'portal_type_Section_description',
                    'content_meta_type': 'Section',
                    'filter_content_types': True},},
            'Workspace': {
                t: 'CPSDefault: Folder (Folder)',
                amt: FTI,
                'properties': {
                    'title': 'portal_type_Workspace_title',
                    'description': 'portal_type_Workspace_description',
                    'content_meta_type': 'Workspace',
                    'filter_content_types': True},},
            'Folder': {
                t: 'CPSDefault: Folder (Folder)',
                amt: FTI,},
            }

        self.verifyContentTypes(type_dict)

        self.allowContentTypes('Workspace', 'Workspace')
        self.allowContentTypes('Section', 'Section')

    def setupRoots(self):
        """Check site and workspaces needed proxies."""

        self.log("Verifying roots: %s and %s" % (SECTIONS_ID, WORKSPACES_ID))
        if not self.portalHas(WORKSPACES_ID):
            self.log("  Adding %s Folder" % WORKSPACES_ID)
            self.portal.portal_workflow.invokeFactoryFor(
                self.portal.this(), 'Workspace', WORKSPACES_ID)

        workspaces = self.portal[WORKSPACES_ID]
        if getattr(self.portal[WORKSPACES_ID], MEMBERS_ID, None) is None:
            self.log("  Adding %s Folder" % MEMBERS_ID)
            self.portal.portal_workflow.invokeFactoryFor(
                workspaces,'Workspace', MEMBERS_ID)

        if not self.portalHas(SECTIONS_ID):
            self.log("  Adding %s Folder" % SECTIONS_ID)
            self.portal.portal_workflow.invokeFactoryFor(
                self.portal.this(), 'Section', SECTIONS_ID)

    def setupRootsi18n(self):
        """Creating the appropriate language revisions for default roots

        Has to be called after roots setup, and after message catalog,
        translation service and translations setup.
        """
        # XXX should probably use the use_mcat property on proxies, see #867
        translation_service = self.portal.translation_service
        avail_langs = translation_service.getSupportedLanguages()

        workspaces = self.portal[WORKSPACES_ID]
        root_titles = [
            (workspaces, WORKSPACES_ID + '_root_title'),
            (workspaces[MEMBERS_ID], MEMBERS_ID + '_root_title'),
            (self.portal[SECTIONS_ID], SECTIONS_ID + '_root_title'),
            ]
        for proxy, title_msgid in root_titles:
            existing_lang_revs = proxy.getLanguageRevisions().keys()
            for lang in avail_langs:
                if lang not in existing_lang_revs:
                    proxy.addLanguageToProxy(lang)
                if self.is_creation or lang not in existing_lang_revs:
                    doc = proxy.getEditableContent(lang)
                    title = translation_service(msgid=title_msgid,
                                                target_language=lang,
                                                default=title_msgid)
                    if isinstance(title, unicode):
                        title = title.encode('ISO-8859-15', 'ignore')
                    doc.setTitle(title)

    def fixupRoots(self):
        """Commit the data model of those folders that were not created through
        the CPSDocument framework due to bootstrap problems.
        """
        workspaces = self.portal[WORKSPACES_ID]
        for proxy in (workspaces,
                      workspaces[MEMBERS_ID],
                      self.portal[SECTIONS_ID]):
            existing_lang_revs = proxy.getLanguageRevisions().keys()
            for lang in existing_lang_revs:
                doc = proxy.getEditableContent(lang)
                dm = doc.getTypeInfo().getDataModel(doc, proxy)
                for k, v in dm.items():
                    dm[k] = v
                dm._commit(check_perms=0)

    def setupTreesTool(self):
        self.verifyTool('portal_trees', 'CPSCore', 'CPS Trees Tool')
        trtool = self.portal.portal_trees
        self.log("Verifying cache trees")
        if SECTIONS_ID not in trtool.objectIds():
            self.log("  Adding cache for tree %s" % SECTIONS_ID)
            trtool.manage_addCPSTreeCache(id=SECTIONS_ID)
            trtool[SECTIONS_ID].manage_changeProperties(
                title=SECTIONS_ID+' Cache',
                root=SECTIONS_ID,
                type_names=('Section',),
                meta_types=('CPS Proxy Folder',
                            'CPS Proxy Document',
                            'CPS Proxy Folderish Document',
                            'CPS Proxy BTree Folder',
                            'CPS Proxy BTree Folderish Folder',
                            ),
                info_method='getFolderInfo')
            self.flagRebuildTreeCache(SECTIONS_ID)

        if WORKSPACES_ID not in trtool.objectIds():
            self.log("  Adding cache for tree %s" % WORKSPACES_ID)
            trtool.manage_addCPSTreeCache(id=WORKSPACES_ID)
            trtool[WORKSPACES_ID].manage_changeProperties(
                title=WORKSPACES_ID+' Cache',
                root=WORKSPACES_ID,
                type_names=('Workspace',),
                meta_types=('CPS Proxy Folder',
                            'CPS Proxy Document',
                            'CPS Proxy Folderish Document',
                            'CPS Proxy BTree Folder',
                            'CPS Proxy BTree Folderish Folder',
                            ),
                info_method='getFolderInfo')
            self.flagRebuildTreeCache(WORKSPACES_ID)

    def setupPortlets(self):
        self.verifyTool('portal_cpsportlets',
                        'CPSPortlets', 'CPS Portlets Tool')
        self.log("Adding cps default portlets")
        portlets = (
               # Front page
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
               # top tabs
               {'type': 'Custom Portlet',
                'slot': 'toptabs',
                'custom_cache_params': [],
                'order': 0,
                'render_method': 'generic_lib_accessibility',
                'Title': 'Hidden access keys',
                },
               {'type': 'Navigation Portlet',
                'slot': 'toptabs',
                'end_depth': 3,
                'display': 'site_map',
                'Title': 'Navigation tabs',
               },
               {'type': 'Breadcrumbs Portlet',
                'slot': 'top',
                'display': 'horizontal_trail',
                'order': 0,
                'Title': 'Breadcrumbs',
                },
               # Left column
               {'type': 'Custom Portlet',
                'slot': 'left',
                'order': 0,
                'custom_cache_params': ['user', 'current_lang'],
                'render_method': 'portlet_session_info',
                'Title': 'Session',
               },
               {'type': 'Language Portlet',
                'slot': 'left',
                'action': 'change',
                'Title': 'Language selector',
                'order': 2,
                },
               {'type': 'Actions Portlet',
                'slot': 'left',
                'order': 10,
                'categories': ['user'],
                'Title': 'User actions',
               },
               {'type': 'Actions Portlet',
                'slot': 'left',
                'order': 20,
                'categories': ['global'],
                'Title': 'Portal actions',
                },
               {'type': 'Navigation Portlet',
                'slot': 'left',
                'order': 50,
                'display': 'navigation_tree',
                'show_icons': 1,
                'Title': 'Navigation',
                },
               # Main column
               {'type': 'Navigation Portlet',
                'slot': 'center_top',
                'visibility_range': [1, 0],
                'display': 'up_to_parent',
                'order': 10,
                'Title': 'Navigation Portlet',
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
                'display_hidden_folders': 1,
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
               # Right column
               {'type': 'Actions Portlet',
                'slot': 'right',
                'order': 10,
                'categories': ['folder'],
                'Title': 'Folder actions',
                },
               {'type': 'Actions Portlet',
                'slot': 'right',
                'order': 0,
                'categories': ['object', 'workflow'],
                'Title': 'Object actions',
                },
               # Bottom slots
               {'type': 'Text Portlet',
                'slot': 'bottom',
                'Title': 'Copyright',
                'text': '<a href="http://www.cps-project.org/">CPS</a> is Copyright &copy; 2002-2005 by <a href="http://www.nuxeo.com/">Nuxeo</a><br/><a href="http://www.medic.chalmers.se/~jmo/CPS/">CPSSkins</a> is Copyright &copy; 2003-2005 by <a href="http://www.medic.chalmers.se/~jmo/">Jean-Marc Orliaguet</a>.',
                'text_format': 'normal',
                'text_position': 'html',
                'order': 0,
                },
               {'type': 'Custom Portlet',
                'slot': 'bottom',
                'custom_cache_params': ['baseurl'],
                'order': 10,
                'render_method': 'portlet_contact_info',
                'Title': 'Contact Info',
                },
               {'type': 'Custom Portlet',
                'slot': 'bottom2',
                'custom_cache_params': [],
                'order': 10,
                'render_method': 'portlet_conformance_statement',
                'Title': 'Conformance statement',
                },

        )
        self.verifyPortlets(portlets)

    def setupi18n(self):
        if not self.portalHas('Localizer'):
            self.log(" Adding Localizer")
            languages = self.langs_list or ('en',)
            self.portal.manage_addProduct['Localizer'].manage_addLocalizer(
                title='',
                languages=languages)

        # translation_service
        if not self.portalHas('translation_service'):
            self.portal.manage_addProduct['TranslationService'].\
                addPlacefulTranslationService(id='translation_service')
            self.log("  translation_service tool added")
            translation_service = self.portal.translation_service
            translation_service.manage_setDomainInfo(path_0='Localizer/default')
            self.log("   default domain set to Localizer/default")

        self.verifyMessageCatalog('default', 'CPSDefault messages')

        # Method handy to reimport translations, but not really necessary.
        if not self.portalHas('i18n Updater'):
            self.log('Creating i18n Updater Support')
            i18n_updater = ExternalMethod('i18n Updater',
                                        'i18n Updater',
                                        'CPSDefault.cpsinstall',
                                        'cps_i18n_update')
            self.portal._setObject('i18n Updater', i18n_updater)

    def setupCPSProducts(self):
        self.setupProduct('CPSUtil')
        self.setupProduct('CPSCollector')
        self.setupProduct('FCKeditor')
        self.setupProduct('CPSDocument')
        self.setupProduct('CPSMailboxer')
        self.setupProduct('CPSRSS')
        self.setupProduct('CPSForum')
        self.setupProduct('CPSChat')
        self.setupProduct('CPSDirectory')
        self.setupProduct('CPSNavigation')
        self.setupProduct('CPSSubscriptions')
        self.setupProduct('CPSSharedCalendar')
        self.setupProduct('CPSNewsLetters')
        self.setupProduct('CPSWiki')

        self.setupProduct('CPSPortlets')
        self.setupProduct('CPSSkins')

        # FIXME: This code makes things hard to test
        try:
            # Trying all the specific imports on which CPSOOo relies
            import xml.dom.minidom
            import xml.dom.ext
            try:
                from elementtree.ElementTree import ElementTree
            except ImportError:
                from lxml.etree import ElementTree
        except ImportError, err:
            self.log("CPSOOo cannot be installed because there are some "
                     "dependencies missing: %s" % str(err))
        else:
            self.setupProduct('CPSOOo')


    def setupCustomDocuments(self):
        """Setup custom widgets/schemas/layouts/vocabularies.

        Setup the needed components for the advanced search form.
        """
        # Reloading the modules to have the latest definitions present
        # on the file system without having to restart Zope.
        reload(schemas)
        reload(layouts)
        reload(vocabularies)

        self.log("Installing custom schemas")
        custom_schemas = schemas.getSchemas()
        self.verifySchemas(custom_schemas)

        self.log("Installing custom layouts")
        custom_layouts = layouts.getLayouts()
        self.verifyLayouts(custom_layouts)

        self.log("Installing custom vocabularies")
        custom_vocabularies = vocabularies.getVocabularies()
        self.verifyVocabularies(custom_vocabularies)

    def setupCachingPolicyManager(self):
        """Configure a default Caching Policy Manager to add HTTP headers on
        images in skins
        """
        if getattr(self.portal, 'caching_policy_manager', None) is not None:
            self.log('Keeping existing Caching Policy Manager')
            return

        self.log('Adding a new Caching Policy Manager with a default policy')
        self.portal.manage_addProduct['CMFCore'
                ].manage_addCachingPolicyManager()
        cpm = self.portal.caching_policy_manager
        predicate = "python:getattr(object, 'meta_type', '') in %s" % str(
                self.DEFAULT_CACHED_META_TYPES)
        cpm.addPolicy(
            'cps_default_meta_types_policy', # Some id
            predicate,         # predicate        TALES expr
            'object/modified', # mtime_func       TALES expr
            3600,              # max_age_secs     integer, seconds (def. 0)
            0,                 # no_cache         boolean (def. 0)
            0,                 # no_store         boolean (def. 0)
            0,                 # must_revalidate  boolean (def. 0)
            '',                # vary             string value
            '',                # etag_func        TALES expr (def. '')
            )



    def doUpgrades(self, post_update=True):
        """Do automatic upgrades."""
        from Products.CPSDefault.Extensions import upgrade
        reload(upgrade)
        DEFAULT = '3.2.0' # If we've never upgraded, start there

        self.log("Checking for upgrades")
        portal = self.portal
        propid = 'last_upgraded_version'
        if not portal.hasProperty(propid):
            # Manually add a property to the instance
            portal._properties += tuple([p for p in portal.__class__._properties
                                         if p['id'] == propid])
            portal.last_upgraded_version = ''
        if not portal.last_upgraded_version:
            portal.last_upgraded_version = DEFAULT

        for prev, next, method, when in upgrade.AUTOMATIC_UPGRADES:
            if prev != '*' and portal.last_upgraded_version != prev:
                continue
            if when.startswith('before') and post_update:
                continue
            if when.startswith('after') and not post_update:
                continue
            self.log(" Upgrading from %s to %s" % (prev, next))
            if method is not None:
                res = method(portal)
                self.log(res)
            if prev != '*':
                portal.last_upgraded_version = next
            #transaction.commit()


def cpsupdate(self, langs_list=None, is_creation=0):
    # helpers
    installer = DefaultInstaller(self)

    # Disable useless subscribers during installation
    installer.disableEventSubscriber('portal_trees')
    installer.disableEventSubscriber('portal_subscriptions')

    installer.install(langs_list, is_creation)

    # Re-enable subscribers
    installer.enableEventSubscriber('portal_trees')
    installer.enableEventSubscriber('portal_subscriptions')

    installer.finalize()
    return installer.logResult()


def cps_i18n_update(self, langs_list=None):
    """
    Importation of the po files for internationalization.
    For CPS Default itself.

    this does not reset the mcat.
    """
    # langs_list is deprecated as it is set in the Localizer
    installer = CPSInstaller(self, 'CPS Default i18n import')
    installer.log("CPSDefault i18n update")
    installer.setupTranslations(product_name='CPSDefault')
    installer.log("CPSDefault i18n update Finished")
    return installer.logResult()
