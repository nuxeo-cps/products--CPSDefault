# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" here we go
"""

import os
import sys
from AccessControl import getSecurityManager
from zLOG import LOG, INFO, DEBUG
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent, \
     ReviewPortalContent, RequestReview
from Products.PythonScripts.PythonScript import PythonScript

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
        if aclu.meta_type == 'User Folder With Groups':
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

    #
    # NuxMetaDirectories
    #
    if not portalhas('portal_metadirectories'):
        pr(" Creating CMF MetaDirectories Tool")
        portal.manage_addProduct["NuxMetaDirectories"].manage_addTool('CMF MetaDirectories Tool')

    mtool = portal.portal_metadirectories
    if "members" not in mtool.objectIds():
        pr("  Adding Member Areas : member")
        mtool.manage_addProduct['NuxMetaDirectories'].manage_addMembersDirectory(id='members',title='Members')
    if "groups" not in mtool.objectIds():
        pr("  Adding Group Directory : group")
        mtool.manage_addProduct['NuxMetaDirectories'].manage_addGroupsDirectory(id='groups', title='Groups')

    # Synchronization with MemberData
    mtool = portal.portal_metadirectories
    mtool.members.syncSchemaAndMemberData()

    # Verification of the action and addinf if neccesarly
    action_found = 0
    for action in portal['portal_actions'].listActions():
        if action.id == 'directories':
            action_found = 1

    if not action_found:
        portal['portal_actions'].addAction(
            id='directories',
            name='Directories',
            action='string: ${portal_url}/directories',
            condition='python:not portal.portal_membership.isAnonymousUser()',
            permission=('View',),
            category='global',
            visible=1)
        pr(" Added Action Directories")

    # skins
    pr("Verifying skins")
    skins = ('cps_nuxeo_style', 'cps_styles', 'cps_images', 'cps_devel',
             'cps_default', 'cps_javascript', 'cps_nuxmetadirectories',
             'cmf_zpt_calendar', 'cmf_calendar')
    paths = {
        'cps_nuxeo_style': 'Products/CPSDefault/skins/cps_styles/nuxeo',
        'cps_styles': 'Products/CPSDefault/skins/cps_styles',
        'cps_images': 'Products/CPSDefault/skins/cps_images',
        'cps_devel': 'Products/CPSDefault/skins/cps_devel',
        'cps_default': 'Products/CPSDefault/skins/cps_default',
        'cps_javascript': 'Products/CPSDefault/skins/cps_javascript',
        'cps_nuxmetadirectories' : 'Products/NuxMetaDirectories/skins/cps_nuxmetadirectories',
        'cmf_zpt_calendar': 'Products/CMFCalendar/skins/zpt_calendar',
        'cmf_calendar': 'Products/CMFCalendar/skins/calendar',
    }
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
            # Update for inner dev version
            # Perhaps not necessarly afterwords ??
            if skin == 'cps_nuxmetadirectories':
                if getattr(portal.portal_skins, 'nuxmetadirectories', None) != None:
                    pr(" Removing the old skins directory for NuxMetaDirectory")
                    portal.portal_skins.manage_delObjects(['nuxmetadirectories'])
            else:
                pass
        else:
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
        from Products.ExternalMethod.ExternalMethod import ExternalMethod
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
    pr("Setup workflow shemas")
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

    for s in ('work', ):
        wf.states.addState(s)

    # create_folder is transition which does nothing?
    for t in ('create', 'create_content', 'create_folder', 'cut_copy_paste'):
        wf.transitions.addTransition(t)

    s = wf.states.get('work')
    s.setProperties(title='Work',
                    transitions=('create_content', 'cut_copy_paste'))
    t = wf.transitions.get('create')
    t.setProperties(title='Initial creation', new_state_id='work',
                    transition_behavior=(TRANSITION_INITIAL_CREATE, ),
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='workflow', actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
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
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
                           'guard_expr':''},
                    )
    # For the cut/copy/paste feature
    t = wf.transitions.get('cut_copy_paste')
    t.setProperties(title='Cut/Copy/Paste', new_state_id='work',
                    transition_behavior=(TRANSITION_ALLOWSUB_DELETE,
                                         TRANSITION_ALLOWSUB_MOVE,
                                         TRANSITION_ALLOWSUB_COPY),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
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

    for s in ('work', 'draft', 'locked'):
        wf.states.addState(s)
    for t in ('create', 'copy_submit',
              'checkout_draft', 'checkout_draft_in', 'checkin_draft',
              'abandon_draft', 'unlock', 'cut_copy_paste'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time',
              'dest_container'):
        wf.variables.addVariable(v)
    for p in (View, ModifyPortalContent, ):
        wf.addManagedPermission(p)

    s = wf.states.get('work')
    s.setProperties(title='Work',
                    transitions=('copy_submit', 'checkout_draft', 'cut_copy_paste'))
    s.setPermission(ModifyPortalContent, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember', 'Owner', ))
    s.setPermission(View, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'))

    s = wf.states.get('draft')
    s.setProperties(title='Draft',
                    transitions=('checkin_draft', 'abandon_draft'))
    s.setPermission(ModifyPortalContent, 0, ('Manager', 'WorkspaceManager', 'Owner'))
    s.setPermission(View, 0, ('Manager', 'WorkspaceManager', 'Owner'))

    s = wf.states.get('locked')
    s.setProperties(title='Locked',
                    transitions=('unlock',))
    s.setPermission(ModifyPortalContent, 0, ('Manager', 'WorkspaceManager'))
    s.setPermission(View, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'))

    t = wf.transitions.get('create')
    t.setProperties(title='Initial creation', new_state_id='work',
                    transition_behavior=(TRANSITION_INITIAL_CREATE, ),
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='workflow', actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
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
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
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
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
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
    t.setProperties(title='Cut/Copy/Paste', new_state_id='work',
                    transition_behavior=(TRANSITION_ALLOWSUB_DELETE,
                                         TRANSITION_ALLOWSUB_MOVE,
                                         TRANSITION_ALLOWSUB_COPY),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
                           'guard_expr':''},
                    )


    # wf scripts
    scripts = wf.scripts

    script_name = 'unlock_locked_before_abandon'
    scripts._setObject(script_name, PythonScript(script_name))
    script = scripts[script_name]
    script.write("""\
##parameters=state_change
# Unlock the locked object before a draft is abandonned.
wftool = context.portal_workflow
object = state_change.object
folder = object.aq_parent
docid = object.getDocid()
flr = object.getFromLanguageRevisions()
locked_ob = None
for ob in folder.objectValues():
    try:
        rs = wftool.getInfoFor(ob, 'review_state', None)
        if (rs == 'locked' and
            ob.getDocid() == docid and
            ob.getLanguageRevisions() == flr):
            locked_ob = ob
            break
    except:
        from zLOG import LOG, DEBUG
        LOG('unlock_locked_before_checkin', DEBUG, 'exception in folder=%s' % folder)
        raise
if locked_ob is not None:
    wftool.doActionFor(locked_ob, 'unlock')
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

    for s in ('work', ):
        wf.states.addState(s)
    for t in ('create', 'copy_submit', 'create_content', 'cut_copy_paste'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time',
              'dest_container'):
        wf.variables.addVariable(v)
    for p in (View, ModifyPortalContent, ):
        wf.addManagedPermission(p)

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
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
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
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
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
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
                           'guard_expr':''},
                    )

    # For the cut/copy/paste feature
    t = wf.transitions.get('cut_copy_paste')
    t.setProperties(title='Cut/Copy/Paste', new_state_id='work',
                    transition_behavior=(TRANSITION_ALLOWSUB_DELETE,
                                         TRANSITION_ALLOWSUB_MOVE,
                                         TRANSITION_ALLOWSUB_COPY),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
                    actbox_name='New',
                    actbox_category='',
                    actbox_url='',
                    props={'guard_permissions':'',
                           'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; ',
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

    for s in ('work', ):
        wf.states.addState(s)
    for t in ('create', 'create_content', 'cut_copy_paste'):
        wf.transitions.addTransition(t)

    s = wf.states.get('work')
    s.setProperties(title='Work',
                    transitions=('create_content', 'cut_copy_paste'))
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
    t.setProperties(title='Cut/Copy/Paste', new_state_id='work',
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

    for s in ('pending', 'published'):
        wf.states.addState(s)
    for t in ('submit', 'publish', 'accept', 'reject', 'unpublish', 'cut_copy_paste'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time',
              'dest_container'):
        wf.variables.addVariable(v)
    for p in (View, ModifyPortalContent, ):
        wf.addManagedPermission(p)

    s = wf.states.get('pending')
    s.setProperties(title='Waiting for reviewer',
                    transitions=('accept', 'reject'))
    s.setPermission(ModifyPortalContent, 0, ('SectionReviewer', 'SectionManager', 'Manager'))
    s.setPermission(View, 0, ('SectionReviewer', 'SectionManager', 'Manager'))

    s = wf.states.get('published')
    s.setProperties(title='Public',
                    transitions=('unpublish', 'cut_copy_paste'))
    s.setPermission(ModifyPortalContent, 0, ('Manager', ))
    s.setPermission(View, 0, ('SectionReader', 'SectionReviewer', 'SectionManager', 'Manager'))

    t = wf.transitions.get('publish')
    t.setProperties(title='Member publishes directly',
                    new_state_id='published',
                    transition_behavior=(TRANSITION_INITIAL_PUBLISHING,
                                         TRANSITION_BEHAVIOR_FREEZE,),
                    clone_allowed_transitions=None,
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

    # For the cut/copy/paste feature
    t = wf.transitions.get('cut_copy_paste')
    t.setProperties(title='Cut/Copy/Paste', new_state_id='work',
                    transition_behavior=(TRANSITION_ALLOWSUB_DELETE,
                                         TRANSITION_ALLOWSUB_MOVE,
                                         TRANSITION_ALLOWSUB_COPY),
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION,
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

    # setup portal_type: CPS Proxy Document, CPS Proxy Folder
    # CPS Folder
    pr("Verifying portal types")
    ttool = portal.portal_types
    if 'Workspace' in ttool.objectIds():
        workspaceACT = list(ttool['Workspace'].allowed_content_types)
    else:
        workspaceACT = []
    for ptype in ('Workspace', 'Dummy',):
        if ptype not in  workspaceACT:
            workspaceACT.append(ptype)

    ptypes = {
        'CPSCore':('CPS Proxy Document',
                   'CPS Proxy Folder',
                   'CPS Proxy Folderish Document',
                   ),
        'CPSDefault':('Folder',
                      'Dummy',
                      'Base Box',
                      'Text Box',
                      'Tree Box',
                      'Content Box',
                      'Action Box',
                      'Image Box',
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
                                             content_meta_type='Section')

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
                                               content_meta_type='Workspace')
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
    # Test for the ModifyWorkspaceContent permission
    # XXX : Why sould I do this for that ??
    # Don't really see the usefullness
    #
    from Products.CMFCore.CMFCorePermissions import setDefaultRoles
    ModifyWorkspaceContent = 'Modify Workspace Content'
    setDefaultRoles( ModifyWorkspaceContent, ( 'Manager', 'WorkspaceManager', 'WorkspaceMember', ))

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
        'View': ['Manager', 'SectionManager', 'SectionReviewer', 'SectionReader'],
        'View management screens': ['Manager', 'SectionManager'],
        }
    workspaces_perm = {
        'Add portal content': ['Manager', 'WorkspaceManager', 'WorkspaceMember', ],
        'Add portal folders': ['Manager', 'WorkspaceManager'],
        'Change permissions': ['Manager', 'WorkspaceManager'],
        'Delete objects': ['Manager', 'WorkspaceManager', 'WorkspaceMember', ],
        'List folder contents': ['Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'],
        'Modify portal content': ['Manager', 'WorkspaceManager', 'WorkspaceMember', 'Owner'],
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
        wfc.manage_addChain(portal_type='Dummy',
                            chain='workspace_content_wf')

    if not '.cps_workflow_configuration' in portal[sections_id].objectIds():
        pr("  Adding workflow configuration to %s" % sections_id)
        portal[sections_id].manage_addProduct['CPSCore'].addCPSWorkflowConfiguration()
        wfc = getattr(portal[sections_id], '.cps_workflow_configuration')
        wfc.manage_addChain(portal_type='Workspace',
                            chain='')
        wfc.manage_addChain(portal_type='Section',
                            chain='section_folder_wf')
        wfc.manage_addChain(portal_type='Dummy',
                            chain='section_content_wf')
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
    action_found = 0
    for action in  portal['portal_actions'].listActions():
        if action.id == 'status_history':
            action_found = 1
    if not action_found:
        portal['portal_actions'].addAction(
            id='status_history',
            name='action_status_history',
            action='string: ${object/absolute_url}/content_status_history',
            condition='python: folder is not object',
            permission='View',
            category='workflow')
        pr(" Added")
    else:
        pr(" Present")


    pr(" Adding cps default boxes")
    idbc = portal.portal_boxes.getBoxContainerId(portal)
    pr("  Checking /%s" % idbc )
    if not portalhas(idbc):
        pr("   Creating")
        portal.manage_addProduct['CPSDefault'].addBoxContainer()
    boxes = {
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


    #
    # i18n Updater
    #

    if not portalhas('i18n Updater'):
        from Products.ExternalMethod.ExternalMethod import ExternalMethod
        pr('Creating i18n Updater Support')
        i18n_updater = ExternalMethod('i18n Updater',
                                      'i18n Updater',
                                      'CPSDefault.cpsinstall',
                                      'cps_i18n_update')
        portal._setObject('i18n Updater', i18n_updater)

    #
    # i18n
    #
    log_i18n = cps_i18n_update(self, langs_list)
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

def cps_i18n_update(self, langs_list=None):
    """
    Importation of the po files for internationalization.
    For CPS itself and compulsory products.
    """
    _log = []
    def pr(bla, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla):
            LOG('cps_i18n_update:', INFO, bla)

    def primp(pr=pr):
        pr(" !!! Cannot migrate that component !!!")

    def prok(pr=pr):
        pr(" Already correctly installed")

    portal = self.portal_url.getPortalObject()
    def portalhas(id, portal=portal):
        return id in portal.objectIds()

    pr(" Updating i18n support")

    # Localizer
    if not portalhas('Localizer'):
        pr("  Adding Localizer")
        languages = langs_list or ('en',)
        portal.manage_addProduct['Localizer'].manage_addLocalizer(
            title='',
            languages=languages,
        )
    else:
        pr("Localizer already here")
    Localizer = portal['Localizer']

    # languages
    languages = Localizer.get_supported_languages()

    # MessageCatalog
    if 'default' in Localizer.objectIds():
        Localizer.manage_delObjects(['default'])
        pr("  previous default MessageCatalog deleted")
    Localizer.manage_addProduct['Localizer'].manage_addMessageCatalog(
        id='default',
        title='CPSDefault messages',
        languages=languages,
    )
    pr("  default MessageCatalogCreated")
    defaultCatalog = Localizer.default

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
        except NameError:
            pr("    %s file not found" % po_path)
        else:
            defaultCatalog.manage_import(lang, po_file)
            pr("    %s file imported" % po_path)

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

    ###################################################
    # i18n for NuxMetaDIrectories
    # Use of a Localizer message Catalog.
    ###################################################

    pr(" Adding i18n support for NuxMetaDirectories")
    metadir_catalog_id = 'cpsmetadirectories'

    Localizer = portal['Localizer']
    languages = Localizer.get_supported_languages()

    # Message Catalog
    if metadir_catalog_id in Localizer.objectIds():
        Localizer.manage_delObjects([metadir_catalog_id])
        pr(" Previous default MessageCatalog deleted for NuxMetaDirectories")

    # Adding the new message Catalog
    Localizer.manage_addProduct['Localizer'].manage_addMessageCatalog(
        id=metadir_catalog_id,
        title='NuxMetaDirectories messages',
        languages=languages,
        )

    pr(" NuxMetaDirectories MessageCatalogCreated")

    defaultCatalog = getattr(Localizer, metadir_catalog_id, None)

    # Working now on the po files
    product_path = sys.modules['Products.NuxMetaDirectories'].__path__[0]
    i18n_path = os.path.join(product_path, 'i18n')
    pr(" po files for NuxMetaDirectories are searched in %s" % i18n_path)
    pr(" po files for NuxMetaDirectories %s are expected" % str(languages))

    # loading po files
    for lang in languages:
        po_filename = lang + '.po'
        pr("   importing %s file" % po_filename)
        po_path = os.path.join(i18n_path, po_filename)
        try:
            po_file = open(po_path)
        except NameError:
            pr("    %s file not found" % po_path)
        po_path = os.path.join(i18n_path, po_filename)
        try:
            po_file = open(po_path)
        except NameError:
            pr("    %s file not found" % po_path)
        else:
            pr("  before  %s file imported" % po_path)
            defaultCatalog.manage_import(lang, po_file)
            pr("    %s file imported" % po_path)

    # Translation Service Tool

    if portalhas('translation_service'):
        translation_service = portal.translation_service
        pr (" Translation Sevice Tool found in here ")

        try:
            if getattr(portal['translation_service'], metadir_catalog_id, None) == None:
                # translation domains
                translation_service.manage_addDomainInfo(metadir_catalog_id,
                                                         'Localizer/'+metadir_catalog_id)
                pr(" cpsmetadirecties domain set to Localizer/cpsmetadirecties")
        except:
            pass
    else:
        raise str('DependanceError'), 'translation_service'

    ######################################################
    # End of i18n for NuxMetaDirectories
    ######################################################

    pr("i18n Update Done")
    return pr('flush')
