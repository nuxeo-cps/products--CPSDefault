# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" here we go
"""

import os
import sys
from Globals import package_home
from AccessControl import getSecurityManager
from zLOG import LOG, INFO, DEBUG
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent, \
     ReviewPortalContent, RequestReview
from Products.PythonScripts.PythonScript import PythonScript
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.CMFCore.Expression import Expression

from Products.CPSCore.CPSWorkflow import \
     TRANSITION_INITIAL_PUBLISHING, TRANSITION_INITIAL_CREATE, \
     TRANSITION_ALLOWSUB_CREATE, TRANSITION_ALLOWSUB_PUBLISHING, \
     TRANSITION_BEHAVIOR_PUBLISHING, TRANSITION_BEHAVIOR_FREEZE, \
     TRANSITION_BEHAVIOR_DELETE, TRANSITION_BEHAVIOR_MERGE, \
     TRANSITION_ALLOWSUB_CHECKOUT, TRANSITION_INITIAL_CHECKOUT, \
     TRANSITION_BEHAVIOR_CHECKOUT, TRANSITION_ALLOW_CHECKIN, \
     TRANSITION_BEHAVIOR_CHECKIN, TRANSITION_ALLOWSUB_DELETE, \
     TRANSITION_ALLOWSUB_MOVE, TRANSITION_ALLOWSUB_COPY

from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from Products.CPSDefault import cpsdefault_globals
from Products.CMFCore.utils import minimalpath
from Products.CPSCore.CPSCorePermissions import ChangeSubobjectsOrder

def cpsinstall(self):
    """
    Cleanup and change stuff from a fresh CMF.
    Do this only once...
    """
    _log = []
    def pr(bla, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla):
            LOG('cpsinstall:', INFO, bla)

    pr("Starting install")
    pr("")
    installername = getSecurityManager().getUser().getUserName()
    pr("Current user: %s" % installername)
    portal = self.portal_url.getPortalObject()

    pr("Cleaning actions")
    actiondelmap = {
        'portal_actions': ('folderContents', 'folder_contents'),
        'portal_syndication': ('syndication',),
        }
    for tool, actionids in actiondelmap.items():
        actions = list(portal[tool]._actions)
        for ac in actions:
            id = ac.id
            if id in actionids:
                if ac.visible:
                    ac.visible = 0
                    pr(" Deleting %s: %s" % (tool, id))
        portal[tool]._actions = actions

    pr("Install Done")
    return pr('flush')


def cpsupdate(self, langs_list=None):
    # helpers
    _log = []
    def pr(bla, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla):
            LOG('cpsupdate:', INFO, bla)

    def primp(pr=pr):
        pr(" !!! Cannot migrate that component !!!")

    def prok(pr=pr):
        pr(" Already correctly installed")

    portal = self.portal_url.getPortalObject()
    def portalhas(id, portal=portal):
        return id in portal.objectIds()


    pr("Starting update")
    pr("")
    installername = getSecurityManager().getUser().getUserName()
    pr("Current user: %s" % installername)

    # setting roles
    pr("Verifying roles")
    already = portal.valid_roles()
    for role in ('WorkspaceManager', # manage: sub object, user right, document, ask for publication
                 'WorkspaceMember',  # manage: document, ask for publication
                 'WorkspaceReader',  # only view documents
                 'SectionManager',   # manage sub object, accept publication
                 'SectionReviewer',  # accept/reject publication
                 'SectionReader',    # only view published document
                 ):
        if role not in already:
            portal._addRole(role)
            pr(" Add role %s" % role)

    # acl_users with group
    pr("Verifying User Folder")
    if portalhas('acl_users'):
        aclu = portal.acl_users
        if aclu.meta_type in ['User Folder With Groups',
                              'LDAPUserGroupsFolder']:
            prok()
        else:
            usernames = aclu.getUserNames()
            if usernames:
                pr(" !!! User Folder already contains users")
                primp()
            else:
                portal.manage_delObjects(['acl_users'])
    if not portalhas('acl_users'):
        pr(" Creating User Folder With Groups")
        portal.manage_addProduct['NuxUserGroups'].addUserFolderWithGroups()

    # portal registration
    if not hasattr(portal, 'enable_portal_joining'):
        portal.manage_addProperty('enable_portal_joining', 1, 'boolean')

    for action in portal['portal_registration'].listActions():
        if action.id == 'join':
            action.condition = Expression('python: portal.portal_properties.enable_portal_joining and not member')

    # portal membership
    pr("Verifying Portal Membership tool")
    if portalhas('portal_membership'):
        pm = portal.portal_membership
        if pm.portal_type == 'CPS Membership Tool':
            prok()
        else:
            portal.manage_delObjects(['portal_membership'])

    if not portalhas('portal_membership'):
        pr(" Creating CPS Membership Tool")
        portal.manage_addProduct['CPSCore'].addCPSMembershipTool()

    # Verification of the action and addinf if neccesarly
    action_found = 0
    for action in portal['portal_actions'].listActions():
        if action.id == 'action_my_preferences':
            action_found = 1

    if not action_found:
        portal['portal_actions'].addAction(
            id='action_my_preferences',
            name='action_my_preferences',
            action="string:${portal_url}/cpsdirectory_entry_view?dirname=members&id=${member}",
            condition='member',
            permission=('View',),
            category='user',
            visible=1)
        pr(" Added Action My Preferences")


    
    # adding more actions
    actions = {
        'accessibility': {'id': 'accessibility',
                          'name': 'action_accessibility',
                          'action': 'string: ${portal_url}/accessibility',
                          'permission': ('View', ),
                          'condition': '',
                          'category': 'global_header',
                          'visible': 1,
                          },
        'print': {'id': 'print',
                  'name': 'action_print',
                  'action':
                  'string:javascript:if (window.print) window.print();',
                  'permission': ('View',),
                  'condition': '',
                  'category': 'global_header',
                  'visible': 1
               },
        'advanced_search': {'id': 'advanced_search',
                            'name': 'action_advanced_search',
                            'action': 'string: ./advanced_search_form',
                            'permission': ('View', ),
                            'condition': '',
                            'category': 'global_header',
                            'visible': 1,
                            },
        'contact': {'id': 'contact',
                    'name': 'action_contact',
                    'action': 'string:mailto:${portal/portal_properties/email_from_address}?subject=Info',
                    'permission': ('View', ),
                    'condition': '',
                    'category': 'global_header',
                    'visible': 1,
                    },
     }
    actions_list = ('accessibility', 'advanced_search', 'print',
                    'contact')

    present_actions = [action.id for action in \
                       portal['portal_actions'].listActions()]

    for action in actions_list:
        if action not in present_actions:
            portal['portal_actions'].addAction(**actions[action])
            pr(" Added Action %s" % action)

    # skins
    pr("Verifying skins")
    skins = ('cps_nuxeo_style', 'cps_styles', 'cps_images', 'cps_devel',
             'cps_default', 'cps_javascript', 'cmf_zpt_calendar',
             'cmf_calendar')
    paths = {
        'cps_nuxeo_style': 'Products/CPSDefault/skins/cps_styles/nuxeo',
        'cps_styles': 'Products/CPSDefault/skins/cps_styles',
        'cps_images': 'Products/CPSDefault/skins/cps_images',
        'cps_devel': 'Products/CPSDefault/skins/cps_devel',
        'cps_default': 'Products/CPSDefault/skins/cps_default',
        'cps_javascript': 'Products/CPSDefault/skins/cps_javascript',
        'cmf_zpt_calendar': 'Products/CMFCalendar/skins/zpt_calendar',
        'cmf_calendar': 'Products/CMFCalendar/skins/calendar',
    }
    skins_to_delete = ('calendar', 'zpt_calendar')

    for skin in skins:
        path = paths[skin]
        path = path.replace('/', os.sep)
        pr(" FS Directory View '%s'" % skin)
        if skin in portal.portal_skins.objectIds():
            dv = portal.portal_skins[skin]
            oldpath = dv.getDirPath()
            if oldpath == path:
                prok()
            else:
                pr("  Correctly installed, correcting path")
                dv.manage_properties(dirpath=path)
        else:
            # XXX: Hack around a CMFCore/DirectoryView bug (?)
            path = os.path.join(package_home(cpsdefault_globals),
                 "..", "..", path)
            path = minimalpath(path)

            portal.portal_skins.manage_addProduct['CMFCore'].manage_addDirectoryView(filepath=path, id=skin)
            pr("  Creating skin")
    allskins = portal.portal_skins.getSkinPaths()
    for skin_name, skin_path in allskins:
        if skin_name != 'Basic':
            continue
        path = [x.strip() for x in skin_path.split(',')]
        path = [x for x in path if x not in skins] # strip all
        if path and path[0] == 'custom':
            path = path[:1] + list(skins) + path[1:]
        else:
            path = list(skins) + path
        npath = ', '.join(path)
        portal.portal_skins.addSkinSelection(skin_name, npath)
        pr(" Fixup of skin %s" % skin_name)

    # Delete useless skin (they get in the way of object creation).
    for skin in skins_to_delete:
        if skin in portal.portal_skins.objectIds():
            portal.portal_skins._delObject(skin)

    pr(" Resetting skin cache")
    portal._v_skindata = None
    portal.setupCurrentSkin()

    pr(" Checking portal_catalog indexes")
    indexes = {
        }
    metadata = [
        ]
    catalog = portal.portal_catalog
    for ix, typ in indexes.items():
        if ix in catalog.Indexes.objectIds():
            pr("  %s: ok" % ix)
        else:
            prod = catalog.Indexes.manage_addProduct['PluginIndexes']
            constr = getattr(prod, 'manage_add%s' % typ)
            constr(ix)
            pr("  %s: added" % ix)


    # CMF Tools
    pr("")
    pr("### CMFCalendar update")
    if not portalhas('cmfcalendar_installer'):
        if portalhas('portal_calendar'):
            portal.manage_delObjects(['portal_calendar'])
        pr('Adding cmfcalendar installer')
        cmfcalendar_installer = ExternalMethod('cmfcalendar_installer',
                                               'CMFCalendar Updater',
                                               'CMFCalendar.Install',
                                               'install')
        portal._setObject('cmfcalendar_installer', cmfcalendar_installer)
        pr(portal.cmfcalendar_installer())
    pr("### End of CMFCalendar update")
    pr("")

    # add tools (CPS Tools): CPS Event Service Tool, CPS Proxies Tool,
    # CPS Object Repository, Tree tools
    pr("Verifying CPS Tools")
    if portalhas('portal_eventservice'):
        prok()
    else:
        pr(" Creating portal_eventservice")
        portal.manage_addProduct["CPSCore"].manage_addTool(
            'CPS Event Service Tool')
    if portalhas('portal_proxies'):
        prok()
    else:
        pr(" Creating portal_proxies")
        portal.manage_addProduct["CPSCore"].manage_addTool('CPS Proxies Tool')
    if portalhas('portal_repository'):
        prok()
    else:
        pr(" Creating portal_repository")
        portal.manage_addProduct["CPSCore"].manage_addTool(
            'CPS Repository Tool')

    if portalhas('portal_trees'):
        prok()
    else:
        pr(" Creating (CPS Tools) CPS Trees Tool")
        portal.manage_addProduct["CPSCore"].manage_addTool('CPS Trees Tool')
    if portalhas('portal_boxes'):
        prok()
    else:
        pr(" Creating portal_boxes")
        portal.manage_addProduct["CPSDefault"].manage_addTool('CPS Boxes Tool')

    # configure event service to hook the proxies, by adding a subscriber
    pr("Verifying Event service tool")
    objs = portal.portal_eventservice.objectValues()
    subscribers = []
    for obj in objs:
        subscribers.append(obj.subscriber)
    if 'portal_proxies' in subscribers:
        prok()
    else:
        pr(" Creation portal_proxies subscribers")
        portal.portal_eventservice.manage_addSubscriber(
            subscriber='portal_proxies',
            action='proxy',
            meta_type='*',
            event_type='*',
            notification_type='synchronous')
    if 'portal_trees' in subscribers:
        prok()
    else:
        pr(" Creation portal_proxies subscribers")
        portal.portal_eventservice.manage_addSubscriber(
            subscriber='portal_trees',
            action='tree',
            meta_type='*',
            event_type='*',
            notification_type='synchronous')


    # replace portal_workflow with a (CPS Tools) CPW Workflow Tool.
    pr("Verifying portal_workflow")
    if portalhas('portal_workflow'):
        if portal.portal_workflow.meta_type == 'CPS Workflow Tool':
            prok()
        else:
            pr(" Removing CMF Workflow Tool")
            portal.manage_delObjects(['portal_workflow'])

    if not portalhas('portal_workflow'):
        pr(" Creating (CPS Tools) CPS Workflow Tool")
        portal.manage_addProduct["CPSCore"].manage_addTool('CPS Workflow Tool')


    # create workflow
    pr("Setup workflow schemas")
    wftool = portal.portal_workflow
    wfids = wftool.objectIds()

    # WF workspace
    wfid = 'workspace_folder_wf'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    wf.addManagedPermission(View)

    for s in ('work', ):
        wf.states.addState(s)

    for t in ('create', 'create_content', 'cut_copy_paste'):
        wf.transitions.addTransition(t)

    s = wf.states.get('work')
    s.setProperties(title='Work',
                    transitions=('create_content', 'cut_copy_paste'))
    s.setPermission(View, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'))

    t = wf.transitions.get('create')
    t.setProperties(title='Initial creation', new_state_id='work',
                    transition_behavior=(TRANSITION_INITIAL_CREATE, ),
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='workflow', actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('create_content')
    t.setProperties(title='Create content', new_state_id='work',
                    transition_behavior=(TRANSITION_ALLOWSUB_CREATE,
                                         TRANSITION_ALLOWSUB_CHECKOUT),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )
    # For the cut/copy/paste feature
    t = wf.transitions.get('cut_copy_paste')
    t.setProperties(title='Cut/Copy/Paste', new_state_id='',
                    transition_behavior=(TRANSITION_ALLOWSUB_DELETE,
                                         TRANSITION_ALLOWSUB_MOVE,
                                         TRANSITION_ALLOWSUB_COPY),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )

    # WF workspace content
    wfid = 'workspace_content_wf'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    for p in (View, ModifyPortalContent):
        wf.addManagedPermission(p)

    for s in ('work', 'draft', 'locked'):
        wf.states.addState(s)
    for t in ('create', 'copy_submit',
              'checkout_draft', 'checkout_draft_in', 'checkin_draft',
              'abandon_draft', 'unlock', 'cut_copy_paste'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time',
              'dest_container'):
        wf.variables.addVariable(v)

    s = wf.states.get('work')
    s.setProperties(title='Work',
                    transitions=('copy_submit', 'checkout_draft', 'cut_copy_paste'))
    s.setPermission(ModifyPortalContent, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember', 'Owner', ))
    s.setPermission(View, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'))

    s = wf.states.get('draft')
    s.setProperties(title='Draft',
                    transitions=('checkin_draft', 'abandon_draft', 'unlock'))
    s.setPermission(ModifyPortalContent, 0, ('Manager', 'WorkspaceManager', 'Owner'))
    s.setPermission(View, 0, ('Manager', 'WorkspaceManager', 'Owner'))

    s = wf.states.get('locked')
    s.setProperties(title='Locked',
                    transitions=('unlock',))
    s.setPermission(ModifyPortalContent, 0, ())
    s.setPermission(View, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'))

    t = wf.transitions.get('create')
    t.setProperties(title='Initial creation', new_state_id='work',
                    transition_behavior=(TRANSITION_INITIAL_CREATE, ),
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='workflow', actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('copy_submit')
    t.setProperties(title='Copy content into a section for Publishing',
                    new_state_id='',
                    transition_behavior=(TRANSITION_BEHAVIOR_PUBLISHING, ),
                    clone_allowed_transitions=('submit', 'publish'),
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='action_submit', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_submit_form',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('checkout_draft')
    t.setProperties(title='Checkout content into a draft',
                    new_state_id='locked',
                    transition_behavior=(TRANSITION_BEHAVIOR_CHECKOUT,),
                    checkout_allowed_initial_transitions=('checkout_draft_in',),
                    actbox_name='action_checkout_draft', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_checkout_draft_form',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('checkout_draft_in')
    t.setProperties(title='Draft is created',
                    new_state_id='draft',
                    transition_behavior=(TRANSITION_INITIAL_CHECKOUT,
                                         TRANSITION_BEHAVIOR_FREEZE),
                    )
    t = wf.transitions.get('checkin_draft')
    t.setProperties(title='Checkin draft',
                    new_state_id='locked',
                    transition_behavior=(TRANSITION_BEHAVIOR_CHECKIN,),
                    checkin_allowed_transitions=('unlock',),
                    actbox_name='action_checkin_draft', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_checkin_draft_form',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; Owner',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('abandon_draft')
    t.setProperties(title='Abandon draft',
                    new_state_id='',
                    transition_behavior=(TRANSITION_BEHAVIOR_DELETE,),
                    script_name='unlock_locked_before_abandon',
                    actbox_name='action_abandon_draft', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_abandon_draft_form',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; Owner',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('unlock')
    t.setProperties(title='Unlock content after a draft is done',
                    new_state_id='work',
                    transition_behavior=(TRANSITION_ALLOW_CHECKIN,),
                    )

    # For the cut/copy/paste feature
    t = wf.transitions.get('cut_copy_paste')
    t.setProperties(title='Cut/Copy/Paste', new_state_id='',
                    transition_behavior=(TRANSITION_ALLOWSUB_DELETE,
                                         TRANSITION_ALLOWSUB_MOVE,
                                         TRANSITION_ALLOWSUB_COPY),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )


    # wf scripts
    scripts = wf.scripts

    script_name = 'unlock_locked_before_abandon'
    scripts._setObject(script_name, PythonScript(script_name))
    script = scripts[script_name]
    script.write("""\
##parameters=state_change
return state_change.object.content_unlock_locked_before_abandon(state_change)
""")
    #script._proxy_roles = ('Manager',)
    script._owner = None

    # wf variables
    wf.variables.setStateVar('review_state')
    vdef = wf.variables['action']
    vdef.setProperties(description='The last transition',
                       default_expr='transition/getId|nothing',
                       for_status=1, update_always=1)

    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed '
                       'the last transition',
                       default_expr='user/getId',
                       for_status=1, update_always=1)

    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_expr="python:state_change.kwargs.get('comment', '')",
                       for_status=1, update_always=1)

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_expr="state_change/getHistory",
                       props={'guard_permissions':'',
                              'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; WorkspaceReader',
                              'guard_expr':''})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

    vdef = wf.variables['dest_container']
    vdef.setProperties(description='Destination container for the last paste/publish',
                       default_expr="python:state_change.kwargs.get('dest_container', '')",
                       for_status=1, update_always=1)

    # WF workspace folderish content
    wfid = 'workspace_folderish_content_wf'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    for p in (View, ModifyPortalContent):
        wf.addManagedPermission(p)

    for s in ('work', ):
        wf.states.addState(s)
    for t in ('create', 'copy_submit', 'create_content', 'cut_copy_paste'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time',
              'dest_container'):
        wf.variables.addVariable(v)

    s = wf.states.get('work')
    s.setProperties(title='Work',
                    transitions=('copy_submit', 'create_content', 'cut_copy_paste'))
    s.setPermission(ModifyPortalContent, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember', ))
    s.setPermission(View, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'))

    t = wf.transitions.get('create')
    t.setProperties(title='Initial creation', new_state_id='work',
                    transition_behavior=(TRANSITION_INITIAL_CREATE, ),
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='workflow', actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('copy_submit')
    t.setProperties(title='Copy content into a section for Publishing',
                    new_state_id='',
                    transition_behavior=(TRANSITION_BEHAVIOR_PUBLISHING, ),
                    clone_allowed_transitions=('submit', 'publish'),
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='action_submit', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_submit_form',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('create_content')
    t.setProperties(title='Create content', new_state_id='work',
                    transition_behavior=(TRANSITION_ALLOWSUB_CREATE, ),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )

    # For the cut/copy/paste feature
    t = wf.transitions.get('cut_copy_paste')
    t.setProperties(title='Cut/Copy/Paste', new_state_id='',
                    transition_behavior=(TRANSITION_ALLOWSUB_DELETE,
                                         TRANSITION_ALLOWSUB_MOVE,
                                         TRANSITION_ALLOWSUB_COPY),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember',
                           'guard_expr':''},
                    )

    # wf variables
    wf.variables.setStateVar('review_state')
    vdef = wf.variables['action']
    vdef.setProperties(description='The last transition',
                       default_expr='transition/getId|nothing',
                       for_status=1, update_always=1)

    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed '
                       'the last transition',
                       default_expr='user/getId',
                       for_status=1, update_always=1)

    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_expr="python:state_change.kwargs.get('comment', '')",
                       for_status=1, update_always=1)

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_expr="state_change/getHistory",
                       props={'guard_permissions':'',
                              'guard_roles':'Manager; WorkspaceManager; WorkspaceMember;  WorkspaceReader',
                              'guard_expr':''})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

    vdef = wf.variables['dest_container']
    vdef.setProperties(description='Destination container for the last paste/publish',
                       default_expr="python:state_change.kwargs.get('dest_container', '')",
                       for_status=1, update_always=1)



    # WF section
    wfid = 'section_folder_wf'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    wf.addManagedPermission(View)

    for s in ('work', ):
        wf.states.addState(s)
    for t in ('create', 'create_content', 'cut_copy_paste'):
        wf.transitions.addTransition(t)

    s = wf.states.get('work')
    s.setProperties(title='Work',
                    transitions=('create_content', 'cut_copy_paste'))
    s.setPermission(View, 0, ('Manager', 'SectionManager', 'SectionReviewer', 'SectionReader'))

    t = wf.transitions.get('create')
    t.setProperties(title='Initial creation', new_state_id='work',
                    transition_behavior=(TRANSITION_INITIAL_CREATE, ),
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='workflow', actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; SectionManager',
                           'guard_expr':''},
                    )
    # XXX: TODO warning guard for publishing and creating sub section are the same
    t = wf.transitions.get('create_content')
    t.setProperties(title='Create a content', new_state_id='',
                    transition_behavior=(TRANSITION_ALLOWSUB_CREATE, TRANSITION_ALLOWSUB_PUBLISHING, ),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='', actbox_category='', actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; SectionManager; SectionReviewer; SectionReader',
                           'guard_expr':''},
                    )

    # For the cut/copy/paste feature
    t = wf.transitions.get('cut_copy_paste')
    t.setProperties(title='Cut/Copy/Paste', new_state_id='',
                    transition_behavior=(TRANSITION_ALLOWSUB_DELETE,
                                         TRANSITION_ALLOWSUB_MOVE,
                                         TRANSITION_ALLOWSUB_COPY),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; SectionManager; SectionReviewer; SectionReader',
                           'guard_expr':''},
                    )

    # WF section content
    wfid = 'section_content_wf'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    for p in (View, ModifyPortalContent):
        wf.addManagedPermission(p)

    for s in ('pending', 'published'):
        wf.states.addState(s)
##     for t in ('submit', 'publish', 'accept', 'reject', 'unpublish',
##               'cut_copy_paste', 'publish_content',):
    for t in ('submit', 'publish', 'accept', 'reject', 'unpublish',
              'cut_copy_paste',):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time',
              'dest_container'):
        wf.variables.addVariable(v)

    s = wf.states.get('pending')
    s.setProperties(title='Waiting for reviewer',
                    transitions=('accept', 'reject'))
    s.setPermission(ModifyPortalContent, 0, ('SectionReviewer', 'SectionManager', 'Manager'))
    s.setPermission(View, 0, ('SectionReviewer', 'SectionManager', 'Manager'))

    s = wf.states.get('published')
##     s.setProperties(title='Public',
##                     transitions=('unpublish', 'cut_copy_paste', 'publish_content',))
    s.setProperties(title='Public',
                    transitions=('unpublish', 'cut_copy_paste',))
    s.setPermission(ModifyPortalContent, 0, ('Manager', ))
    s.setPermission(View, 0, ('SectionReader', 'SectionReviewer', 'SectionManager', 'Manager'))

    t = wf.transitions.get('publish')
    t.setProperties(title='Member publishes directly',
                    new_state_id='published',
                    transition_behavior=(TRANSITION_INITIAL_PUBLISHING,
                                         TRANSITION_BEHAVIOR_FREEZE,),
                    clone_allowed_transitions=None,
                    after_script_name='mail_notification',
                    actbox_name='', actbox_category='', actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; SectionManager; SectionReviewer',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('submit')
    t.setProperties(title='Member requests publishing',
                    new_state_id='pending',
                    transition_behavior=(TRANSITION_INITIAL_PUBLISHING,
                                         TRANSITION_BEHAVIOR_FREEZE),
                    clone_allowed_transitions=None,
                    after_script_name='mail_notification',
                    actbox_name='', actbox_category='', actbox_url='',
                    props={'guard_permissions': '',
                           'guard_roles': 'Manager; Member',
                           'guard_expr': ''},
                    )
    t = wf.transitions.get('accept')
    t.setProperties(title='Reviewer accepts publishing',
                    new_state_id='published',
                    transition_behavior=(TRANSITION_BEHAVIOR_MERGE,),
                    clone_allowed_transitions=None,
                    after_script_name='mail_notification',
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='action_accept', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_accept_form',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; SectionManager; SectionReviewer',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('reject')
    t.setProperties(title='Reviewer rejects publishing',
                    new_state_id='',
                    transition_behavior=(TRANSITION_BEHAVIOR_DELETE,),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='action_reject', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_reject_form',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; SectionManager; SectionReviewer',
                           'guard_expr':''},
                    )
    t = wf.transitions.get('unpublish')
    t.setProperties(title='Reviewer removes content from publication',
                    new_state_id='',
                    transition_behavior=(TRANSITION_BEHAVIOR_DELETE,),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='action_un_publish', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_unpublish_form',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; SectionManager; SectionReviewer',
                           'guard_expr':''},
                    )
##     t = wf.transitions.get('publish_content')
##     t.setProperties(title='Publish a subcontent', new_state_id='',
##                     transition_behavior=(TRANSITION_ALLOWSUB_PUBLISHING, ),
##                     clone_allowed_transitions=None,
##                     trigger_type=TRIGGER_USER_ACTION,
##                     actbox_name='', actbox_category='', actbox_url='',
##                     props={'guard_permissions':'',
##                            'guard_roles':'Manager; SectionManager; SectionReviewer; SectionReader',
##                            'guard_expr':''},
##                     )

    # For the cut/copy/paste feature
    t = wf.transitions.get('cut_copy_paste')
    t.setProperties(title='Cut/Copy/Paste', new_state_id='',
                    transition_behavior=(TRANSITION_ALLOWSUB_DELETE,
                                         TRANSITION_ALLOWSUB_MOVE,
                                         TRANSITION_ALLOWSUB_COPY),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    after_script_name='mail_notification',
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; SectionManager; SectionReviewer',
                           'guard_expr':''},
                    )

    # wf variables
    wf.variables.setStateVar('review_state')
    vdef = wf.variables['action']
    vdef.setProperties(description='The last transition',
                       default_expr='transition/getId|nothing',
                       for_status=1, update_always=1)

    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed '
                       'the last transition',
                       default_expr='user/getId',
                       for_status=1, update_always=1)

    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_expr="python:state_change.kwargs.get('comment', '')",
                       for_status=1, update_always=1)

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_expr="state_change/getHistory",
                       props={'guard_roles':'Manager; SectionManager; SectionReviewer; SectionReader' } )

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

    vdef = wf.variables['dest_container']
    vdef.setProperties(description='Destination container for the last copy/publish',
                       default_expr="python:state_change.kwargs.get('dest_container', '')",
                       for_status=1, update_always=1)

    #
    # Python Script.
    # For Mailing List notifications
    #
    scripts = wf.scripts

    script_name = 'mail_notification'
    scripts._setObject(script_name, PythonScript(script_name))
    script = scripts[script_name]
    script.write("""\
##parameters=state_change
object = state_change.object
dest_container = state_change.kwargs.get('dest_container', '')

try:
    # Mailing Lists package in here
    object.sendmail_after_transition(destination = dest_container)
except:
    # No mailing list package in here.
    pass
""")
    #script._proxy_roles = ('Manager',)
    script._owner = None

    # setup portal_type: CPS Proxy Document, CPS Proxy Folder
    # CPS Folder
    pr("Verifying portal types")
    ttool = portal.portal_types
    if 'Workspace' in ttool.objectIds():
        workspaceACT = list(ttool['Workspace'].allowed_content_types)
    else:
        workspaceACT = []
    for ptype in ('Workspace',): # forget about 'Dummy' for now
        if ptype not in  workspaceACT:
            workspaceACT.append(ptype)

    ptypes = {
        'CPSCore':('CPS Proxy Document',
                   'CPS Proxy Folder',
                   'CPS Proxy Folderish Document',
                   ),
        'CPSDefault':('Folder',
                      #'Dummy',
                      'Base Box',
                      'Text Box',
                      'Tree Box',
                      'Content Box',
                      'Action Box',
                      'Image Box',
                      'Flash Box',
                      'Event Calendar Box',
                      )
        }
    allowed_content_type = {
                            'Section' : ('Section',),
                            'Workspace' : workspaceACT,
                            }

    ptypes_installed = ttool.objectIds()

    for prod in ptypes.keys():
        for ptype in ptypes[prod]:
            pr("  Type '%s'" % ptype)
            if ptype in ptypes_installed:
                ttool.manage_delObjects([ptype])
                pr("   Deleted")

            ttool.manage_addTypeInformation(
                id=ptype,
                add_meta_type='Factory-based Type Information',
                typeinfo_name=prod+': '+ptype,
                )
            pr("   Installation")

    # add Section and Workspace portal types based on CPS Proxy Folder
    if 'Section' in ptypes_installed:
        pr("  Type Section Deleted")
        ttool.manage_delObjects('Section')
    ttool.manage_addTypeInformation(
        id='Section',
        add_meta_type='Factory-based Type Information',
        typeinfo_name='CPSDefault: Folder',
        )
    ttool['Section'].manage_changeProperties(title='portal_type_Section_title',
                                             description='portal_type_Section_description',
                                             content_meta_type='Section',
                                             filter_content_types=1)

    if 'Workspace' in ptypes_installed:
        pr("  Type Workspace Deleted")
        ttool.manage_delObjects('Workspace')
    ttool.manage_addTypeInformation(
        id='Workspace',
        add_meta_type='Factory-based Type Information',
        typeinfo_name='CPSDefault: Folder',
        )
    ttool['Workspace'].manage_changeProperties(title='portal_type_Workspace_title',
                                               description='portal_type_Workspace_description',
                                               content_meta_type='Workspace',
                                               filter_content_types=1)
    for ptype in ('Section', 'Workspace'):
        ttool[ptype].allowed_content_types = allowed_content_type[ptype]


    # check workflow association
    pr("Verifying workflow schemas")
    wfs = {
        'Section': 'section_folder_wf',
        'Workspace': 'workspace_folder_wf',
        }
    wftool = portal.portal_workflow
    pr("Installing workflow schemas")
    for pt, chain in wfs.items():
        wftool.setChainForPortalTypes([pt], chain)
    wftool.setDefaultChain('')

    # check site and workspaces proxies
    sections_id = 'sections'
    workspaces_id = 'workspaces'
    members_id = 'members'

    pr("Verifying roots: %s and %s" % (sections_id, workspaces_id))
    if not portalhas(workspaces_id):
        portal.portal_workflow.invokeFactoryFor(portal.this(), 'Workspace',
                                                workspaces_id)
        portal[workspaces_id].getContent().setTitle('Root of Workspaces') # XXX L10N
        portal[workspaces_id].reindexObject()
        pr("  Adding %s Folder" % workspaces_id)

    # Member areas
    if getattr(portal[workspaces_id], members_id, None) == None:
        workspaces = portal[workspaces_id]
        portal.portal_workflow.invokeFactoryFor(workspaces,'Workspace',
                                                members_id)
        ms = getattr(workspaces, members_id, None)

        ms.getContent().setTitle('Member Areas') # XXX Localization
        ms.reindexObject()
        pr("  Adding %s Folder" % members_id)

    if not portalhas(sections_id):
        portal.portal_workflow.invokeFactoryFor(portal.this(), 'Section',
                                                sections_id)
        portal[sections_id].getContent().setTitle('Root of Sections') # XXX L10N
        portal[sections_id].reindexObject()
        pr("  Adding %s Folder" % sections_id)

    #
    # To avoid the user being able to change the
    # property of the workspace
    #
    from Products.CMFCore.CMFCorePermissions import setDefaultRoles
    ModifyFolderPoperties = 'Modify Folder Properties'
    setDefaultRoles( ModifyFolderPoperties, ( 'Manager', 'WorkspaceManager',))

    pr("Verifying permissions")
    sections_perm = {
        'Request review':['Manager', 'WorkspaceManager', 'WorkspaceMember',  'SectionReviewer', 'SectionManager'],
        'Review portal content':['Manager', 'SectionReviewer', 'SectionManager'],
        'Add Box Container': ['Manager', 'SectionManager'],
        'Manage Box Overrides': ['Manager','SectionManager'],
        'Manage Boxes': ['Manager', 'SectionManager'],
        'Add portal content': ['Manager', 'SectionManager'],
        'Add portal folders': ['Manager', 'SectionManager'],
        'Change permissions': ['Manager', 'SectionManager'],
        'Delete objects': ['Manager', 'SectionManager', 'SectionReviewer'],
        'List folder contents': ['Manager', 'SectionManager', 'SectionReviewer', 'SectionReader'],
        'Modify portal content': ['Manager', 'SectionManager'],
        'Modify Folder Properties' : ['Manager', 'SectionManager'],
        'View': ['Manager', 'SectionManager', 'SectionReviewer', 'SectionReader'],
        'View management screens': ['Manager', 'SectionManager'],
        }
    workspaces_perm = {
        'Add portal content': ['Manager', 'WorkspaceManager', 'WorkspaceMember', ],
        'Add portal folders': ['Manager', 'WorkspaceManager'],
        'Change permissions': ['Manager', 'WorkspaceManager'],
        'Change subobjects order': ['Manager', 'WorkspaceManager', 'WorkspaceMember', ],
        'Delete objects': ['Manager', 'WorkspaceManager', 'WorkspaceMember', ],
        'List folder contents': ['Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'],
        'Modify portal content': ['Manager', 'WorkspaceManager', 'WorkspaceMember', 'Owner'],
        'Modify Folder Properties' : ['Manager', 'WorkspaceManager'],
        'View': ['Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'],
        'View management screens': ['Manager', 'WorkspaceManager', 'WorkspaceMember',],
        'Add Box Container': ['Manager', 'WorkspaceManager', 'SectionManager'],
        'Manage Box Overrides': ['Manager','WorkspaceManager'],
        'Manage Boxes': ['Manager', 'WorkspaceManager'],
        }
    pr("Section")
    for perm, roles in sections_perm.items():
        portal[sections_id].manage_permission(perm, roles, 0)
        pr("  Permission %s" % perm)
    portal[sections_id].reindexObjectSecurity()

    pr("Workspace")
    for perm, roles in workspaces_perm.items():
        portal[workspaces_id].manage_permission(perm, roles, 0)
        pr("  Permission %s" % perm)
    portal[workspaces_id].reindexObjectSecurity()



    pr("Verifying local workflow association")
    if not '.cps_workflow_configuration' in portal[workspaces_id].objectIds():
        pr("  Adding workflow configuration to %s" % workspaces_id)
        portal[workspaces_id].manage_addProduct['CPSCore'].addCPSWorkflowConfiguration()
        wfc = getattr(portal[workspaces_id], '.cps_workflow_configuration')
        wfc.manage_addChain(portal_type='Workspace',
                            chain='workspace_folder_wf')
        wfc.manage_addChain(portal_type='Section',
                            chain='')
        #wfc.manage_addChain(portal_type='Dummy',
        #                    chain='workspace_content_wf')

    if not '.cps_workflow_configuration' in portal[sections_id].objectIds():
        pr("  Adding workflow configuration to %s" % sections_id)
        portal[sections_id].manage_addProduct['CPSCore'].addCPSWorkflowConfiguration()
        wfc = getattr(portal[sections_id], '.cps_workflow_configuration')
        wfc.manage_addChain(portal_type='Workspace',
                            chain='')
        wfc.manage_addChain(portal_type='Section',
                            chain='section_folder_wf')
        #wfc.manage_addChain(portal_type='Dummy',
        #                    chain='section_content_wf')
    # init Tree Tool
    trtool = portal.portal_trees
    pr("Verifying cache trees")
    if sections_id not in trtool.objectIds():
        pr("  Adding cache for tree %s" % sections_id)
        trtool.manage_addCPSTreeCache(id=sections_id)
        trtool[sections_id].manage_changeProperties(
            title=sections_id+' Cache',
            root=sections_id,
            type_names=('Section',),
            meta_types=('CPS Proxy Folder',
                        'CPS Proxy Document',
                        'CPS Proxy Folderish Document',),
            info_method='getFolderInfo')
    trtool[sections_id].manage_rebuild()
    pr("   Sections cache rebuilded")

    if workspaces_id not in trtool.objectIds():
        pr("  Adding cache for tree %s" % workspaces_id)
        trtool.manage_addCPSTreeCache(id=workspaces_id)
        trtool[workspaces_id].manage_changeProperties(
            title=workspaces_id+' Cache',
            root=workspaces_id,
            type_names=('Workspace',),
            meta_types=('CPS Proxy Folder',
                        'CPS Proxy Document',
                        'CPS Proxy Folderish Document',),
            info_method='getFolderInfo')
    trtool[workspaces_id].manage_rebuild()
    pr("   Workspaces cache rebuilded")


    pr("Verifying private area creation flag")
    if not portal.portal_membership.getMemberareaCreationFlag():
        pr(" Activated")
        portal.portal_membership.setMemberareaCreationFlag()
    else:
        prok()

    pr("Verifiying status history action for document")
    #force the update of this action
    index = 0
    for action in  portal['portal_actions'].listActions():
        if action.id == 'status_history':
            portal['portal_actions'].deleteActions((index,))
        index += 1
    portal['portal_actions'].addAction(
        id='status_history',
        name='action_status_history',
        action='string: ${object/absolute_url}/content_status_history',
        # XXX: this is messy.
        condition="python:getattr(object, 'portal_type', None) not in ('Section', 'Workspace', 'Portal', 'Calendar', 'Event')",
        permission='View',
        category='workflow')
    pr(" Added")


    pr("Verifiying bookmark actions (favorites)")
    if 'Link' in portal['portal_types'].objectIds():
        action_addfav_found = 0
        action_viewfav_found = 0
        for action in  portal['portal_actions'].listActions():
            if action.id == 'add_favorites':
                action_addfav_found = 1
            elif action.id == 'view_favorites':
                action_viewfav_found = 1
        if not action_addfav_found:
            portal['portal_actions'].addAction(
                id='add_favorites',
                name='action_add_favorites',
                action='string:${object/absolute_url}/addtoFavorites',
                condition='python: member and portal.portal_membership.getHomeFolder()',
                permission='View',
                category='user')
            pr(" Action add_favorites added")
        else:
            pr(" Action add_favorites present")
        if not action_viewfav_found:
            portal['portal_actions'].addAction(
                id='view_favorites',
                name='action_view_favorites',
                action='string:${portal/portal_membership/getHomeUrl}/Favorites',
                condition='python: hasattr(portal.portal_membership.getHomeFolder(),"Favorites")',
                permission='View',
                category='user')
            pr(" Action view_favorites added")
        else:
            pr(" Action view_favorites present")
    else:
        pr(" CPSDocument type Link does not seem to exist ; Favorites will not be available")

    pr("Adding cps default boxes")
    idbc = portal.portal_boxes.getBoxContainerId(portal)
    pr("  Checking /%s" % idbc )
    if not portalhas(idbc):
        pr("   Creating")
        portal.manage_addProduct['CPSDefault'].addBoxContainer()
    boxes = {
        'action_header': {'type':'Action Box',
                 'title': 'Header actions',
                 'btype': 'header',
                 'slot': 'top',
                 'order': 5,
                 },
        'search': {'type':'Base Box',
                 'title': 'Search form',
                 'btype': 'search',
                 'slot': 'top',
                 'order': 10,
                 },
        'logo': {'type':'Base Box',
                 'title': 'Nuxeo logo',
                 'btype': 'logo',
                 'slot': 'top',
                 'order': 20,
                 },
        'menu': {'type':'Base Box',
                 'title': 'Main menu',
                 'btype': 'menu',
                 'slot': 'top',
                 'order': 30,
                 },
        'breadcrumbs': {'type':'Base Box',
                        'title': 'Bread crumbs',
                        'btype': 'breadcrumbs',
                        'slot': 'top',
                        'order': 40,
                        },

        'footer': {'type': 'Base Box',
                   'title': 'Footer',
                   'btype': 'footer',
                   'slot': 'bottom',
                   'order': 10,
                   },

        'l10n_select': {'type':'Base Box',
                        'title': 'Local selector',
                        'btype': 'l10n_select',
                        'slot': 'left',
                        'order': 10,
                        },

        'action_user': {'type': 'Action Box',
                        'title': 'User actions',
                        'btype': 'user',
                        'slot':'left',
                        'order':20,
                        'categories':'user',
                        },
        'action_portal' : {'type':'Action Box',
                           'title': 'Portal actions',
                           'slot':'left',
                           'order':30,
                           'categories':'global',
                           },
        'navigation': {'type':'Tree Box',
                       'title':'Navigation',
                       'depth':1,
                       'contextual':1,
                       'slot':'left',
                       'order':40},

        'action_object' : {'type':'Action Box',
                           'title': 'Object actions',
                           'slot':'right',
                           'order':10,
                           'categories':('object', 'workflow'),
                           },

        'action_folder' : {'type':'Action Box',
                           'title': 'Folder actions',
                           'slot':'right',
                           'order':20,
                           'categories':'folder',
                           },

        'welcome' : {'type':'Base Box',
                     'title': 'CPS Welcome',
                     'slot':'center',
                     'order':10,
                     'btype':'welcome',
                     'display_in_subfolder': 0,
                     'display_only_in_subfolder': 0,
                     },

        'nav_header' : {'type':'Base Box',
                        'title': 'Folder header',
                        'slot':'folder_view',
                        'order':0,
                        'btype':'folder_header',
                        },

        'nav_folder' : {'type':'Tree Box',
                        'title': 'Sub folder',
                        'slot':'folder_view',
                        'order':10,
                        'box_skin': 'here/box_lib/macros/wbox2',
                        'btype':'center',
                        'contextual':1,
                        'depth':2,
                        'children_only':1,
                        },

        'nav_content' : {'type':'Content Box',
                         'title': 'Contents',
                         'slot':'folder_view',
                         'btype':'default',
                         'box_skin': 'here/box_lib/macros/sbox2',
                         'order':20,
                         },
        }
    box_container = portal[idbc]
    existing_boxes = box_container.objectIds()
    for box in boxes.keys():
        if box in existing_boxes:
            continue
        pr("   Creation of box: %s" % box)
        apply(ttool.constructContent,
              (boxes[box]['type'], box_container,
               box, None), {})
        ob = getattr(box_container, box)
        ob.manage_changeProperties(**boxes[box])

    # Box management action at the root of the portal
    pactions = list(portal['portal_actions']._actions)
    i = 0
    for ac in pactions:
        id = ac.id
        if id == "boxes":
            del pactions[i]
        i+=1
        pr(" Deleting %s: %s" % ('portal_actions', id))
    portal['portal_actions']._actions = pactions

    # Adding it now
    portal['portal_actions'].addAction(
        id='boxes',
        name='action_boxes_root',
        action='string: ${portal_url}/box_manage_form',
        condition='python:folder is object',
        permission=('Manage Boxes',),
        category='global',
        visible=1)
    pr(" Added Action Boxes at global scope ")

    # Localizer - instantiating it before call to other services' installers
    # as they make the asumption that it exists
    if not portalhas('Localizer'):
        pr(" Adding Localizer")
        languages = langs_list or ('en',)
        portal.manage_addProduct['Localizer'].manage_addLocalizer(
            title='',
            languages=languages,
        )
    else:
        pr("Localizer already here")

    # translation_service
    if not portalhas('translation_service'):
        portal.manage_addProduct['TranslationService'].addPlacefulTranslationService(
            id='translation_service'
        )
        pr("  translation_service tool added")
        translation_service = portal.translation_service

        # translation domains

        translation_service.manage_setDomainInfo(path_0='Localizer/default')
        pr("   default domain set to Localizer/default")

    # init the default mcat
    i18n_init_default_mcat(self)

    #
    # i18n Updater
    #
    if not portalhas('i18n Updater'):
        pr('Creating i18n Updater Support')
        i18n_updater = ExternalMethod('i18n Updater',
                                      'i18n Updater',
                                      'CPSDefault.cpsinstall',
                                      'cps_i18n_update')
        portal._setObject('i18n Updater', i18n_updater)


    ###########################################################
    # INSTALLATION OF THE DIFFERENT SERVICES
    ###########################################################

    #
    #  CPSCollector installer/updater
    #
    try:
        import Products.CPSCollector
        if not portalhas('cpscollector_installer'):
            pr('Adding CPSCollector installer')
            cpscollector_installer = ExternalMethod('cpscollector_installer',
                                                    'CPSCollector Installer',
                                                    'CPSCollector.install',
                                                    'install')
            portal._setObject('cpscollector_installer', cpscollector_installer)
        pr(portal.cpscollector_installer())
    except ImportError:
        pass

    #
    #  CPSDocument installer/updater
    #
    try:
        import Products.CPSDocument
        if not portalhas('cpsdocument_installer'):
            pr("Adding CPSDocument installer")
            cpsdocument_installer = ExternalMethod('cpsdocument_installer',
                                              'CPSDocument Installer',
                                              'CPSDocument.install',
                                              'install')
            portal._setObject('cpsdocument_installer', cpsdocument_installer)
        pr(portal.cpsdocument_installer())
    except ImportError:
        pr("!! Could not import or execute CPSDocument installer")


    #
    #  CPSRSS installer/updater
    #
    try:
        import Products.CPSRSS
        if not portalhas('cpsrss_installer'):
            pr('Adding CPSRSS installer')
            cpsrss_installer = ExternalMethod('cpsrss_installer',
                                              'CPSRSS Installer',
                                              'CPSRSS.install',
                                              'install')
            portal._setObject('cpsrss_installer', cpsrss_installer)
        pr(portal.cpsrss_installer())
    except ImportError:
        pass

    #
    #  CPSForum installer/updater
    #
    try:
        import Products.CPSForum
        if not portalhas('cpsforum_installer'):
            pr('Adding CPSForum installer')
            cpsforum_installer = ExternalMethod('cpsforum_installer',
                                                'CPSForum Installer',
                                                'CPSForum.install',
                                                'install')
            portal._setObject('cpsforum_installer', cpsforum_installer)
        pr(portal.cpsforum_installer())
    except ImportError:
        pass

    #
    #  CPSChat installer/updater
    #
    try:
        import Products.CPSChat
        if not portalhas('cpschat_installer'):
            pr('Adding CPSChat installer')
            cpschat_installer = ExternalMethod('cpschat_installer',
                                               'CPSChat Installer',
                                               'CPSChat.install',
                                               'install')
            portal._setObject('cpschat_installer', cpschat_installer)
        pr(portal.cpschat_installer())
    except ImportError:
        pass

    #
    #  CPSCalendar installer/updater
    #
    try:
        import Products.CPSCalendar
        if not portalhas('cpscalendar_installer'):
            pr('Adding cpsdocument installer')
            cpsdocument_installer = ExternalMethod('cpscalendar_installer',
                                                   'CPSCalendar Updater',
                                                   'CPSCalendar.install',
                                                   'update')
            portal._setObject('cpscalendar_installer', cpsdocument_installer)
        pr(portal.cpscalendar_installer())
    except ImportError:
        pass

    #
    #  CPSDirectory installer/updater
    #
    try:
        import Products.CPSDirectory
        if not portalhas('cpsdirectory_installer'):
            pr('Adding cpsdirectory installer')
            cpsdirectory_installer = ExternalMethod('cpsdirectory_installer',
                                                    'CPSDirectory Updater',
                                                    'CPSDirectory.install',
                                                    'install')
            portal._setObject('cpsdirectory_installer', cpsdirectory_installer)
        pr(portal.cpsdirectory_installer())
        # Synchronization from members directory schema to MemberData
        # properties
        mdir = portal.portal_directories.members
        mdir.updateMemberDataFromSchema()
    except ImportError:
        pr("!! Could not import or execute CPSDirectory installer")

    #
    #  CPSMailingLists installer/updater
    #  To be called after cause we are using the default catalog too.
    #
    try:
        import Products.CPSMailingLists
        if not portalhas('cpsml_installer'):
            pr('Adding cpsmailinglists installer')
            cpsml_installer = ExternalMethod('cpsml_installer',
                                                   'CPSMailingLists Updater',
                                                   'CPSMailingLists.install',
                                                   'install')
            portal._setObject('cpsml_installer', cpsml_installer)
        pr(portal.cpsml_installer())
    except ImportError:
        pass

    #
    # setting i18n default
    # this has to be done last as we want CPSDefault override *
    log_i18n = i18n_load_default_mcat(self)
    pr (log_i18n)

    pr(" Reindexing catalog")
    portal.portal_catalog.refreshCatalog(clear=1)

    # remove cpsinstall external method
    # and fix cpsupdate permission
    if 'cpsinstall' in portal.objectIds():
        pr("Removing cpsinstall")
        portal._delObject('cpsinstall')
    if 'cpsupdate' in portal.objectIds():
        pr("Protecting cpsupdate")
        portal.cpsupdate.manage_permission(
            'View', roles=['Manager'], acquire=0
        )
        portal.cpsupdate.manage_permission(
            'Access contents information', roles=['Manager'], acquire=0
        )

    pr("Update Done")
    return pr('flush')



def i18n_init_default_mcat(self):
    """Delete and Create a message catalog Localizer.default."""
    _log = []
    def pr(bla, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla):
            LOG('cps_i18n_init:', INFO, bla)

    pr(" Initialize default i18n support")
    portal = self.portal_url.getPortalObject()
    Localizer = portal['Localizer']
    languages = Localizer.get_supported_languages()

    if 'default' in Localizer.objectIds():
        Localizer.manage_delObjects(['default'])
        pr("  previous default MessageCatalog deleted")

    Localizer.manage_addProduct['Localizer'].manage_addMessageCatalog(
        id='default',
        title='CPSDefault messages',
        languages=languages,
    )
    pr("  default MessageCatalogCreated")
    return pr('flush')


def i18n_load_default_mcat(self):
    """Load *.po from CPSDefault/i18n/ directory."""
    _log = []
    def pr(bla, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla):
            LOG('cps_i18n_update:', INFO, bla)

    pr(" Updating i18n Localizer.default mcat")
    portal = self.portal_url.getPortalObject()
    Localizer = portal['Localizer']
    defaultCatalog = Localizer.default
    languages = Localizer.get_supported_languages()

    # computing po files' system directory
    CPSDefault_path = sys.modules['Products.CPSDefault'].__path__[0]
    i18n_path = os.path.join(CPSDefault_path, 'i18n')
    pr("   po files are searched in %s" % i18n_path)
    pr("   po files for %s are expected" % str(languages))

    # loading po files
    for lang in languages:
        po_filename = lang + '.po'
        pr("   importing %s file" % po_filename)
        po_path = os.path.join(i18n_path, po_filename)
        try:
            po_file = open(po_path)
        except (IOError, NameError):
            pr("    %s file not found" % po_path)
        else:
            defaultCatalog.manage_import(lang, po_file)
            pr("    %s file imported" % po_path)

    pr("i18n Update Done")

    return pr('flush')



def cps_i18n_update(self, langs_list=None):
    """
    Importation of the po files for internationalization.
    For CPS Default itself.

    this does not reset the mcat.
    """
    # langs_list is deprecated as it is set in the Localizer
    text = ''
    text += i18n_load_default_mcat(self)
    return text
