# (C) Copyright 2003-2005 Nuxeo SARL <http://nuxeo.com>
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
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CPSWorkflow.transitions import \
     TRANSITION_INITIAL_PUBLISHING, TRANSITION_INITIAL_CREATE, \
     TRANSITION_ALLOWSUB_CREATE, TRANSITION_ALLOWSUB_PUBLISHING, \
     TRANSITION_BEHAVIOR_PUBLISHING, TRANSITION_BEHAVIOR_FREEZE, \
     TRANSITION_BEHAVIOR_DELETE, TRANSITION_BEHAVIOR_MERGE, \
     TRANSITION_ALLOWSUB_CHECKOUT, TRANSITION_INITIAL_CHECKOUT, \
     TRANSITION_BEHAVIOR_CHECKOUT, TRANSITION_ALLOW_CHECKIN, \
     TRANSITION_BEHAVIOR_CHECKIN, TRANSITION_ALLOWSUB_DELETE, \
     TRANSITION_ALLOWSUB_MOVE, TRANSITION_ALLOWSUB_COPY
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from Products.CPSInstaller.CPSInstaller import CPSInstaller
from Products.CPSDefault.MembershipTool import MembershipTool
try:
    from Products.ExternalEditor.ExternalEditor import ExternalEditorPermission
    external_editor_present = 1
except ImportError:
    external_editor_present = 0

SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'

WebDavLockItem = 'WebDAV Lock items'
WebDavUnlockItem = 'WebDAV Unlock items'

class DefaultInstaller(CPSInstaller):

    product_name = 'CPSDefault'
    DEFAULT_CPS_LEXICON_ID = 'cps_defaut_lexicon'
    DEFAULT_CPS_LEXICON_TITLE = 'CPS Default Lexicon for ZCTextIndex'

    CPS_FILTER_SETS_INDEX = 'cps_filter_sets'
    # this set is supposed to match anything that can be viewed
    # ie anything except document in portal_repository
    CPS_FILTER_SEARCHABLE_SET = 'searchable'
    CPS_FILTER_SEARCHABLE_EXPR = """not filter(lambda s: s.startswith('portal_') or s and s[0] in ('.', '_'), o.getPhysicalPath())"""
    CPS_FILTER_LEAVES_SET = 'leaves'
    CPS_FILTER_LEAVES_EXPR = """getattr(o, 'portal_type', None) not in ('Section', 'Workspace')"""
    # this following filter matches all proxies in their default languages,
    # this is usefull to remove all translations of a same proxy
    # match also all non proxy objects and should be used with searchable set
    CPS_FILTER_DEFAULT_LANGUAGES_SET = 'default_languages'
    CPS_FILTER_DEFAULT_LANGUAGES_EXPR = "not hasattr(o, 'isDefaultLanguage') or o.isDefaultLanguage()"


    WFS_ADD_LANGUAGE_TO_PROXY = {
        'add_language_to_proxy': {
            '_owner': None,
            'script': """\
##parameters=state_change
lang=state_change.kwargs.get('lang')
from_lang=state_change.kwargs.get('from_lang')
state_change.object.addLanguageToProxy(lang, from_lang)
"""
            },
        }


    def install(self, langs_list=None, is_creation=0, interface='portlets'):
        """Main installer
        """
        self._interface = interface
        self.langs_list = langs_list
        self.is_creation = is_creation

        self.log("Starting CPS update")
        self.log("")
        installername = getSecurityManager().getUser().getUserName()
        self.log("Current user: %s" % installername)

        self.setupRegistration()
        self.setupMembership()
        self.setupTools()
        self.setupSkins()
        self.setupEventService()

        # Disable useless subscriber
        self.disableEventSubscriber('portal_trees')
        self.disableEventSubscriber('portal_subscriptions')

        self.setupTypes()
        self.setupActions()
        self.setupWorkflow()
        self.setupRoots()
        self.setupAccessControl()
        self.setupLocalWorkflow()
        self.upgradeWorkflowStatus()
        self.setupTreesTool()
        self.setupBoxes()
        self.setupi18n()
        self.setupCPSProducts()
        if (self.is_creation and
            self._interface == 'portlets'):
            self.setupPortlets()
        self.setupForms()

        self.log("Verifying private area creation flag")
        if not self.portal.portal_membership.getMemberareaCreationFlag():
            self.log(" Activated")
            self.portal.portal_membership.setMemberareaCreationFlag()
        else:
            self.logOK()

        self.setupCatalog()

        # remove cpsinstall external method
        # and fix cpsupdate permission
        if 'cpsinstall' in self.portal.objectIds():
            self.log("Removing cpsinstall")
            self.portal._delObject('cpsinstall')

        self.setupTranslations()
        self.log("CPS update Finished")
        self.verifyVHM()
        
        # Disable useless subscriber
        self.enableEventSubscriber('portal_trees')
        self.enableEventSubscriber('portal_subscriptions')

    #
    # Catalog
    #
    def catalogEnumerateIndexes( self ):
        #   Return a list of ( index_name, type ) pairs for the initial
        #   index set.
        class Struct:
            def __init__(self, **kw):
                for k, v in kw.items():
                    setattr(self, k, v)

        return (('Title', 'FieldIndex', None) # used for sorting
                , ('ZCTitle', 'ZCTextIndex',  # used for searching
                   Struct(doc_attr='Title',
                          lexicon_id=self.DEFAULT_CPS_LEXICON_ID,
                          index_type='Okapi BM25 Rank'))
                , ('Subject', 'KeywordIndex', None)
                , ('Description', 'ZCTextIndex',
                   Struct(doc_attr='Description',
                          lexicon_id=self.DEFAULT_CPS_LEXICON_ID,
                          index_type='Okapi BM25 Rank'))
                , ('Creator', 'FieldIndex', None)
                , ('SearchableText', 'ZCTextIndex',
                   Struct(doc_attr='SearchableText',
                          lexicon_id=self.DEFAULT_CPS_LEXICON_ID,
                          index_type='Okapi BM25 Rank'))
                , ('Date', 'DateIndex', None)
                , ('Type', 'FieldIndex', None)
                , ('created', 'DateIndex', None)
                , ('effective', 'DateIndex', None)
                , ('expires', 'DateIndex', None)
                , ('modified', 'DateIndex', None)
                , ('allowedRolesAndUsers', 'KeywordIndex', None)
                , ('localUsersWithRoles', 'KeywordIndex', None)
                , ('review_state', 'FieldIndex', None)
                , ('in_reply_to', 'FieldIndex', None)
                , ('meta_type', 'FieldIndex', None)
                , ('id', 'FieldIndex', None)
                , ('getId', 'FieldIndex', None)
                , ('path', 'PathIndex', None)
                , ('portal_type', 'FieldIndex', None)
                , (self.CPS_FILTER_SETS_INDEX, 'TopicIndex',
                   (Struct(id=self.CPS_FILTER_SEARCHABLE_SET,
                           expr=self.CPS_FILTER_SEARCHABLE_EXPR),
                    Struct(id=self.CPS_FILTER_LEAVES_SET,
                           expr=self.CPS_FILTER_LEAVES_EXPR),
                    Struct(id=self.CPS_FILTER_DEFAULT_LANGUAGES_SET,
                           expr=self.CPS_FILTER_DEFAULT_LANGUAGES_EXPR),))
                , ('start', 'DateIndex', None)
                , ('end', 'DateIndex', None)
                , ('time', 'DateIndex', None) # time of the last transition
                , ('Language', 'FieldIndex', None)
               )

    def catalogEnumerateMetadata( self ):
        #   Return a sequence of schema names to be cached (catalog metadata).
        #   id is depricated and may go away, use getId!
        return ('Subject'               # CMF metadata
                , 'Title'
                , 'Description'
                , 'Type'
                , 'review_state'
                , 'Creator'
                , 'Date'
                , 'getIcon'
                , 'created'
                , 'effective'
                , 'expires'
                , 'modified'
                , 'CreationDate'
                , 'EffectiveDate'
                , 'ExpirationDate'
                , 'ModificationDate'
                , 'id'
                , 'getId'
                , 'portal_type'
                # CPS metadata
                , 'Contributors'
                , 'Language'
                , 'start'
                , 'end'
                , 'getRevision'
                , 'time'                # time of the last transition
               )

    def setupCatalog(self):
        # check default ZCTextIndex lexicon
        self.addZCTextIndexLexicon(self.DEFAULT_CPS_LEXICON_ID,
                                   self.DEFAULT_CPS_LEXICON_TITLE)
        ct = self.portal.portal_catalog
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
        ModifyFolderPoperties = 'Modify Folder Properties'
        setDefaultRoles(ModifyFolderPoperties,
            ('Manager', 'WorkspaceManager',))

        if external_editor_present:
            portal_perms = {
                ExternalEditorPermission: ['Manager', 'Member'],
                }
            self.setupPortalPermissions(portal_perms, self.portal)
        sections_perms = {
            'Request review': ['Manager', 'WorkspaceManager',
                               'WorkspaceMember', 'Contributor',
                               'SectionReviewer', 'SectionManager'],
            'Review portal content': ['Manager', 'SectionReviewer',
                                      'SectionManager'],
            'Add Box Container': ['Manager', 'SectionManager'],
            'Manage Box Overrides': ['Manager','SectionManager'],
            'Manage Boxes': ['Manager', 'SectionManager'],
            'Add portal content': ['Manager', 'SectionManager', 'Contributor'],
            'Add portal folders': ['Manager', 'SectionManager'],
            'Change permissions': ['Manager', 'SectionManager'],
            'Change subobjects order': ['Manager', 'SectionManager'],
            'Delete objects': ['Manager', 'SectionManager', 'SectionReviewer'],
            'List folder contents': ['Manager', 'SectionManager',
                                     'SectionReviewer', 'SectionReader',
                                     'Contributor'],
            'Modify portal content': ['Manager', 'SectionManager',
                                      'Contributor'],
            'Modify Folder Properties': ['Manager', 'SectionManager'],
            'View': ['Manager', 'SectionManager', 'SectionReviewer',
                     'SectionReader', 'Contributor'],
            'View management screens': ['Manager', 'SectionManager'],
            'View archived revisions': ['Manager', 'SectionManager',
                                        'SectionReviewer', 'Contributor'],
            WebDavLockItem: ['SectionManager', 'SectionReviewer'],
            WebDavUnlockItem: ['SectionManager', 'SectionReviewer'],
            }
        self.setupPortalPermissions(sections_perms, self.portal[SECTIONS_ID])
        workspaces_perms = {
            'Add portal content': ['Manager', 'WorkspaceManager',
                                   'WorkspaceMember', 'Contributor'],
            'Add portal folders': ['Manager', 'WorkspaceManager'],
            'Change permissions': ['Manager', 'WorkspaceManager'],
            'Change subobjects order': ['Manager', 'WorkspaceManager',
                                        'WorkspaceMember', 'Contributor'],
            'Delete objects': ['Manager', 'WorkspaceManager',
                               'WorkspaceMember', 'Contributor'],
            'List folder contents': ['Manager', 'WorkspaceManager',
                                     'WorkspaceMember', 'Contributor', 'WorkspaceReader'],
            'Modify portal content': ['Manager', 'WorkspaceManager',
                                      'WorkspaceMember', 'Contributor', 'Owner'],
            'Modify Folder Properties': ['Manager', 'WorkspaceManager'],
            'View': ['Manager', 'WorkspaceManager', 'WorkspaceMember', 'Contributor',
                     'WorkspaceReader'],
            'View management screens': ['Manager', 'WorkspaceManager',
                                        'WorkspaceMember', 'Contributor'],
            'Add Box Container': ['Manager', 'WorkspaceManager',
                                  'SectionManager'],
            'Manage Box Overrides': ['Manager','WorkspaceManager'],
            'Manage Boxes': ['Manager', 'WorkspaceManager'],
            'View archived revisions': ['Manager', 'WorkspaceManager',
                                        'WorkspaceMember', 'Contributor'],
            WebDavLockItem: ['WorkspaceManager', 'WorkspaceMember', 'Contributor', 'Owner'],
            WebDavUnlockItem: ['WorkspaceManager', 'WorkspaceMember', 'Owner'],
            }
        self.setupPortalPermissions(workspaces_perms, self.portal[WORKSPACES_ID])

        if 'cpsupdate' in self.portal.objectIds():
            self.log("Protecting cpsupdate")
            self.portal.cpsupdate.manage_permission(
                View, roles=['Manager'], acquire=0)
            self.portal.cpsupdate.manage_permission(
                'Access contents information', roles=['Manager'], acquire=0)

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

        self.verifyAction('portal_actions',
                id='action_my_preferences',
                name='action_my_preferences',
                action="string:${portal_url}/cpsdirectory_entry_view?"
                       "dirname=members&id=${member}",
                condition='member',
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

        # Clean old CPS habit.
        if self.hasAction('portal_actions', 'status_history'):
            self.deleteActions({'portal_actions': ('status_history',)})
            self.log("Deleted old 'status_history' action from portal_actions")


    def setupSkins(self):
        self.deleteSkins(('calendar', 'zpt_calendar'))
        skins = {
            'cps_nuxeo_style': 'Products/CPSDefault/skins/cps_styles/nuxeo',
            'cps_styles': 'Products/CPSDefault/skins/cps_styles',
            'cps_images': 'Products/CPSDefault/skins/cps_images',
            'cps_devel': 'Products/CPSDefault/skins/cps_devel',
            'cps_default': 'Products/CPSDefault/skins/cps_default',
            'cps_boxes'  : 'Products/CPSBoxes/skins/cps_boxes',
            'cps_javascript': 'Products/CPSDefault/skins/cps_javascript',
            'cps_default_installer': 'Products/CPSDefault/skins/cps_default_installer',
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
                 'permissions': (View, ModifyPortalContent,
                                 WebDavLockItem, WebDavUnlockItem,),
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
                'title': 'Modification of content,'
                         'provides a specific entry in status history',
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
                            self.WFS_ADD_LANGUAGE_TO_PROXY, {})


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
                'title': 'Modification of content,'
                         'provides a specific entry in status history',
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
        wfscripts.update(self.WFS_ADD_LANGUAGE_TO_PROXY)

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
                'title': 'Modification of content,'
                         'provides a specific entry in status history',
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
                            self.WFS_ADD_LANGUAGE_TO_PROXY, {})

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
                                       'Manager'),
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
                'after_script_name': '',
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
                'after_script_name': '',
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
            'modify': { 'title': 'Modification of content,'
                                 'provides a specific entry in status history',
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
                props={'guard_permissions': 'Modify portal content',
                       'guard_roles': '',
                       'guard_expr': ''})
            self.log("  Added translate")
            work_state = wf.states['work']
            transitions = work_state.transitions
            if not 'translate' in transitions:
                # XXX seems nothing is available for just adding a transition
                work_state.transitions = transitions + ('translate',)
                self.log("  translate activated for %s" % wf.getId())


    def setupTypes(self):
        # setup portal_type: CPS Proxy Document, CPS Proxy Folder
        # CPS Folder
        if self.is_creation:
            # Remove some default CPS types:
            ttool = self.getTool('portal_types')
            ttool.manage_delObjects(['Folder',])

        type_dict = {
            'CPS Proxy Document': {
                       'typeinfo_name': 'CPSCore: CPS Proxy Document',
                       'add_meta_type': 'Factory-based Type Information',},
            'CPS Proxy Folder': {
                       'typeinfo_name': 'CPSCore: CPS Proxy Folder',
                       'add_meta_type': 'Factory-based Type Information',},
            'CPS Proxy Folderish Document': {
                       'typeinfo_name': 'CPSCore: CPS Proxy Folderish Document',
                       'add_meta_type': 'Factory-based Type Information',},
            'CPS Proxy BTree Folder': {
                       'typeinfo_name': 'CPSCore: CPS Proxy BTree Folder',
                       'add_meta_type': 'Factory-based Type Information',},
            'CPS Proxy BTree Folderish Document': {
                       'typeinfo_name': 'CPSCore: CPS Proxy BTree Folderish Document',
                       'add_meta_type': 'Factory-based Type Information',},

            'Section': {
                       'typeinfo_name': 'CPSDefault: Folder',
                       'add_meta_type': 'Factory-based Type Information',
                       'properties': {
                            'title': 'portal_type_Section_title',
                            'description': 'portal_type_Section_description',
                            'content_meta_type': 'Section',
                            'filter_content_types': 1},},
            'Workspace': {
                       'typeinfo_name': 'CPSDefault: Folder',
                       'add_meta_type': 'Factory-based Type Information',
                       'properties': {
                            'title': 'portal_type_Workspace_title',
                            'description': 'portal_type_Workspace_description',
                            'content_meta_type': 'Workspace',
                            'filter_content_types': 1},},
            'Folder': {
                       'typeinfo_name': 'CPSDefault: Folder',
                       'add_meta_type': 'Factory-based Type Information',},
            }

        boxes_dict =  {

            'Base Box': {
                       'typeinfo_name': 'CPSBoxes: Base Box',
                       'add_meta_type': 'Factory-based Type Information',},
            'Text Box': {
                       'typeinfo_name': 'CPSBoxes: Text Box',
                       'add_meta_type': 'Factory-based Type Information',},
            'Tree Box': {
                       'typeinfo_name': 'CPSBoxes: Tree Box',
                       'add_meta_type': 'Factory-based Type Information',},
            'Content Box': {
                       'typeinfo_name': 'CPSBoxes: Content Box',
                       'add_meta_type': 'Factory-based Type Information',},
            'Action Box': {
                       'typeinfo_name': 'CPSBoxes: Action Box',
                       'add_meta_type': 'Factory-based Type Information',},
            'Image Box': {
                       'typeinfo_name': 'CPSBoxes: Image Box',
                       'add_meta_type': 'Factory-based Type Information',},
            'Flash Box': {
                       'typeinfo_name': 'CPSBoxes: Flash Box',
                       'add_meta_type': 'Factory-based Type Information',},
            'Event Calendar Box': {
                       'typeinfo_name': 'CPSBoxes: Event Calendar Box',
                       'add_meta_type': 'Factory-based Type Information',},
            'InternalLinks Box': {
                       'typeinfo_name': 'CPSBoxes: InternalLinks Box',
                       'add_meta_type': 'Factory-based Type Information',},
            'Doc Render Box':{
                       'typeinfo_name': 'CPSBoxes: Doc Render Box',
                       'add_meta_type': 'Factory-based Type Information',},
        }

        self.verifyContentTypes(type_dict)
        self.verifyContentTypes(boxes_dict)

        self.allowContentTypes('Workspace', 'Workspace')
        self.allowContentTypes('Section', 'Section')

    def setupRoots(self):
        # check site and workspaces proxies
        members_id = 'members'

        self.log("Verifying roots: %s and %s" % (SECTIONS_ID, WORKSPACES_ID))
        if not self.portalHas(WORKSPACES_ID):
            self.log("  Adding %s Folder" % WORKSPACES_ID)
            self.portal.portal_workflow.invokeFactoryFor(
                self.portal.this(), 'Workspace', WORKSPACES_ID)
            workspaces = self.portal[WORKSPACES_ID]
            # XXX This should work if workspaces were a true CPSDocument.
            # What is the problem?
            #workspaces.getEditableContent().edit(Title="Workspaces")
            workspaces.getEditableContent().setTitle("Workspaces")
            # XXX Make L10N more generic
            workspaces.addLanguageToProxy('fr')
            workspaces.getEditableContent('fr').setTitle("Espaces de travail")

        if getattr(self.portal[WORKSPACES_ID], members_id, None) is None:
            self.log("  Adding %s Folder" % members_id)
            workspaces = self.portal[WORKSPACES_ID]
            self.portal.portal_workflow.invokeFactoryFor(
                workspaces,'Workspace', members_id)
            member_areas = getattr(workspaces, members_id, None)
            member_areas.getEditableContent().setTitle("Member Areas")
            # XXX Make L10N more generic
            member_areas.addLanguageToProxy('fr')
            member_areas.getEditableContent('fr').setTitle("Espaces des membres")

        if not self.portalHas(SECTIONS_ID):
            self.log("  Adding %s Folder" % SECTIONS_ID)
            self.portal.portal_workflow.invokeFactoryFor(
                self.portal.this(), 'Section', SECTIONS_ID)
            sections = self.portal[SECTIONS_ID]
            sections.getEditableContent().setTitle("Sections")
            # XXX Make L10N more generic
            sections.addLanguageToProxy('fr')
            sections.getEditableContent('fr').setTitle("Espaces de publication")

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
               {'type': 'Custom Portlet',
                'slot': 'left',
                'order': 0,
                'custom_cache_params': ['user', 'current_lang'],
                'render_method': 'portlet_session_info',
                'Title': 'Session',
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
               {'type': 'Text Portlet',
                'slot': 'bottom',
                'Title': 'Copyright',
                'text': '<a href="http://www.cps-project.org/">CPS</a> is Copyright &copy; 2002-2005 by <a href="http://www.nuxeo.com/">Nuxeo</a><br/><a href="http://www.medic.chalmers.se/~jmo/CPS/">CPSSkins</a> is Copyright &copy; 2003-2005 by <a href="http://www.medic.chalmers.se/~jmo/">Jean-Marc Orliaguet</a>.',
                'text_format': 'normal',
                'text_position': 'html',
                'order': 0,
                },
               {'type': 'Custom Portlet',
                'slot': 'bottom2',
                'custom_cache_params': [],
                'order': 10,
                'render_method': 'portlet_conformance_statement',
                'Title': 'Conformance statement',
                },
               {'type': 'Language Portlet',
                'slot': 'left',
                'action': 'change',
                'Title': 'Language selector',
                },
               {'type': 'Navigation Portlet',
                'slot': 'left',
                'order': 50,
                'display': 'navigation_tree',
                'show_icons': 1,
                'Title': 'Navigation',
                },

        )
        self.verifyPortlets(portlets)

    def setupBoxes(self):
        self.verifyTool('portal_boxes', 'CPSBoxes', 'CPS Boxes Tool')
        self.log("Adding cps default boxes")
        boxes = {
            'action_header': {'type': 'Action Box',
                    'title': 'Header actions',
                    'btype': 'header',
                    'slot': 'top',
                    'categories': 'global_header',
                    'order': 5,
                    },
            'search': {'type': 'Base Box',
                    'title': 'Search form',
                    'btype': 'search',
                    'slot': 'top',
                    'order': 10,
                    },
            'logo': {'type': 'Base Box',
                    'title': 'Portal logo',
                    'btype': 'logo',
                    'slot': 'top',
                    'order': 20,
                    },
            'menu': {'type': 'Tree Box',
                    'title': 'Tab menu',
                    'btype': 'menu',
                    'slot': 'top',
                    'order': 30,
                    },
            'breadcrumbs': {'type': 'Base Box',
                            'title': 'Navigation path',
                            'btype': 'breadcrumbs',
                            'slot': 'top',
                            'order': 40,
                            },

            'contact': {'type': 'Text Box',
                       'title': 'Contact',
                       'btype': 'default',
                       'box_skin': 'here/box_lib/macros/wbox2',
                       'slot': 'bottom',
                       'order': 10,
                       'text': '<address class="contact">Nuxeo - 18-20, rue Soleillet, 75020 Paris France<br />Email : <a href="mailto:contact@nuxeo.com">contact@nuxeo.com</a> - Tel: +33 (0)1 40 33 79 87 - Fax: +33 (0)1 40 33 71 41</address>',
                    },

            'conformance_statement': {'type': 'Base Box',
                    'title': 'Conformance statements',
                    'btype': 'conformance_statement',
                    'slot': 'bottom',
                    'order': 20,
                    },

            'l10n_select': {'type': 'Base Box',
                            'title': 'Locale selector',
                            'btype': 'l10n_select',
                            'slot': 'left',
                            'order': 10,
                            },

            'action_user': {'type': 'Action Box',
                            'title': 'User actions',
                            'btype': 'user',
                            'slot': 'left',
                            'order': 20,
                            'categories': 'user',
                            'box_skin': 'here/box_lib/macros/sbox',
                            },
            'action_portal': {'type': 'Action Box',
                            'title': 'Portal actions',
                            'slot': 'left',
                            'order': 30,
                            'categories': 'global',
                            'box_skin': 'here/box_lib/macros/sbox',
                            },
            'navigation': {'type': 'Tree Box',
                        'title': 'Navigation tree menu',
                        'depth': 1,
                        'contextual': 1,
                        'slot': 'left',
                        'order': 40,
                        'box_skin': 'here/box_lib/macros/mmbox',
                        },

            'action_object': {'type': 'Action Box',
                            'title': 'Object actions',
                            'slot': 'right',
                            'order': 10,
                            'categories': ('object', 'workflow'),
                            'box_skin': 'here/box_lib/macros/sbox',
                            },

            'action_folder': {'type': 'Action Box',
                            'title': 'Folder actions',
                            'slot': 'right',
                            'order': 20,
                            'categories': 'folder',
                            },

            'welcome': {'type': 'Text Box',
                        'title': 'Portal welcome message',
                        'slot': 'center',
                        'order': 10,
                        'btype': 'default',
                         # No frame, no title box, no class="box" cf. box_lib.pt
                        'box_skin': 'here/box_lib/macros/wbox3',
                        'display_in_subfolder': 0,
                        'display_only_in_subfolder': 0,
                        'text': 'welcome_body',
                        'i18n': 1,
                        },

            'nav_header': {'type': 'Base Box',
                            'title': 'Folder header',
                            'slot': 'folder_view',
                            'order': 0,
                            'btype': 'folder_header',
                            },

            'nav_folder': {'type': 'Tree Box',
                            'title': 'Sub folders',
                            'slot': 'folder_view',
                            'order': 10,
                            'box_skin': 'here/box_lib/macros/wbox2',
                            'btype': 'center',
                            'contextual': 1,
                            'depth': 2,
                            'children_only': 1,
                            },

            'nav_content': {'type': 'Content Box',
                            'title': 'Contents',
                            'slot': 'folder_view',
                            'btype': 'default',
                            'box_skin': 'here/box_lib/macros/sbox2',
                            'order': 20,
                            },
        }
        self.verifyBoxes(boxes)
        self.verifyAction(
            tool='portal_actions',
            id='boxes',
            name='action_boxes_root',
            action='string:${portal_url}/box_manage_form',
            condition='python:folder is object',
            permission=('Manage Boxes',),
            category='global',
            visible=1)

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
        self.setupProduct('CPSCollector')
        self.setupProduct('CPSDocument')
        self.setupProduct('CPSMailboxer')
        self.setupProduct('CPSRSS')
        self.setupProduct('CPSForum')
        self.setupProduct('CPSChat')
        self.setupProduct('CPSCalendar')
        self.setupProduct('CPSDirectory')
        self.setupProduct('CPSNavigation')
        self.setupProduct('CPSSubscriptions')
        self.setupProduct('CPSNewsLetters')
        self.setupProduct('CPSWiki')
        try:
            from elementtree.ElementTree import ElementTree
        except ImportError, e:
            if str(e) != 'No module named elementtree.ElementTree':
                raise
            self.log("Cannot install CPSOOo: missing elementtree module")
        else:
            self.setupProduct('CPSOOo')

        if ((self.is_creation and
             self._interface == 'portlets') or
            'portal_cpsportlets' in self.portal.objectIds()):
            self.setupProduct('CPSPortlets')
            self.setupProduct('CPSSkins')

    def setupForms(self):
        """Setup Widget/Schema/Layout/Vocabulary used in forms."""
        return cpsdefault_update_forms(self.portal, self)

def cpsupdate(self, langs_list=None, is_creation=0, interface='portlets'):
    # helpers
    installer = DefaultInstaller(self)

    # Disable useless subscriber
    installer.disableEventSubscriber('portal_trees')
    installer.disableEventSubscriber('portal_subscriptions')

    installer.install(langs_list, is_creation, interface=interface)

    # Enable useless subscriber
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


def cpsdefault_update_forms(self, installer=None):
    """Update widget/schemas/layout/vocabularies defined inCPSDefaultForm.

    This method can be define as an external method."""
    return_log = 0
    if installer is None:
        return_log = 1
        installer = CPSInstaller(self, 'CPSDefault Form updater')
    installer.log("CPSDefault update forms start.")
    installer.verifyWidgets(self.getCPSDefaultFormWidgets())
    installer.verifySchemas(self.getCPSDefaultFormSchemas())
    installer.verifyLayouts(self.getCPSDefaultFormLayouts())
    installer.verifyVocabularies(self.getCPSDefaultFormVocabularies())
    installer.log("CPSDefault update forms done.")
    if return_log:
        return installer.logResult()
