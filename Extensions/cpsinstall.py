# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
""" here we go
"""

import os
from random import randrange
from Acquisition import aq_base
from DateTime.DateTime import DateTime
from AccessControl import getSecurityManager
from App.Extensions import getPath
from zLOG import LOG, INFO, DEBUG
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent, \
     ReviewPortalContent, RequestReview

from Products.CPSCore.CPSWorkflow import \
     TRANSITION_INITIAL_PUBLISHING, TRANSITION_INITIAL_CREATE, \
     TRANSITION_ALLOWSUB_CREATE, TRANSITION_ALLOWSUB_PUBLISHING, \
     TRANSITION_BEHAVIOR_PUBLISHING, TRANSITION_BEHAVIOR_FREEZE
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
        'portal_actions': ['folderContents', 'folder_contents'],
        'portal_membership': ['preferences',
                              'addFavorite',
                              'mystuff',
                              'favorites',
                              ],
        'portal_syndication': ['syndication'],
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
        pr(" !!! Can migrate that component !!!")

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

    # skins
    pr("Verifying skins")
    skins = ('cps_styles', 'cps_plone_styles', 'cps_images', 'cps_devel', 'cps_default')
    paths = {
        'cps_styles': 'Products/CPSDefault/skins/cps_styles/nuxeo',
        'cps_plone_styles': 'Products/CPSDefault/skins/cps_styles',
        'cps_images': 'Products/CPSDefault/skins/cps_images',
        'cps_devel': 'Products/CPSDefault/skins/cps_devel',
        'cps_default': 'Products/CPSDefault/skins/cps_default',
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

    pr(" Checking portal_catalog indexes")
    indexes = {
        'is_closed': 'FieldIndex',
        'parent_path': 'FieldIndex',
        'sort_order': 'FieldIndex',
        'xpos': 'FieldIndex',
        'ypos': 'FieldIndex',
        }
    metadata = [
        'is_closed',
        'parent_path',
        'sort_order',
        'xpos', 'ypos',
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
    for t in ('create', 'create_content', 'create_folder'):
        wf.transitions.addTransition(t)

    s = wf.states.get('work')
    s.setProperties(title='Work', 
                    transitions=('create_content',))
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

    # WF workspace content
    wfid = 'workspace_content_wf'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    
    for s in ('work', ):
        wf.states.addState(s)
    for t in ('create', 'copy_submit', ):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for p in (View, ModifyPortalContent, ):
        wf.addManagedPermission(p)
        
    s = wf.states.get('work')
    s.setProperties(title='Work', 
                    transitions=('copy_submit',))
    s.setPermission(ModifyPortalContent, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember'))
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
                    actbox_name='Submit', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_submit_form',
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
                              'guard_roles':'Manager; WorkspaceManager; WorkspaceMember; WorkspaceReader',
                              'guard_expr':''})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
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
    for t in ('create', 'create_content'):
        wf.transitions.addTransition(t)

    s = wf.states.get('work')
    s.setProperties(title='Work', 
                    transitions=('create_content',))
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

    # WF section content
    wfid = 'section_content_wf'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    
    for s in ('pending', 'published' ):
        wf.states.addState(s)
    for t in ('submit', 'publish', 'accept', 'reject', 'unpublish'):        
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
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
                    transitions=('unpublish',))
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
                    transition_behavior=None,
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION, 
                    actbox_name='Accept', actbox_category='workflow', 
                    actbox_url='%(content_url)s/content_accept_form',
                    props={'guard_permissions':'', 
                           'guard_roles':'Manager; SectionManager; SectionReviewer', 
                           'guard_expr':''},
                    )
    t = wf.transitions.get('reject')
    t.setProperties(title='Reviewer rejects publishing',
                    new_state_id='', 
                    transition_behavior=None,
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION, 
                    actbox_name='Reject', actbox_category='workflow', 
                    actbox_url='%(content_url)s/content_reject_form',
                    props={'guard_permissions':'', 
                           'guard_roles':'Manager; SectionManager; SectionReviewer', 
                           'guard_expr':''},
                    )    
    t = wf.transitions.get('unpublish')
    t.setProperties(title='remove content from publication',
                    new_state_id='', 
                    transition_behavior=None,
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION, 
                    actbox_name='Un Publish', actbox_category='workflow', 
                    actbox_url='%(content_url)s/content_unpublish_form',
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

        
    # setup portal_type: CPS Proxy Document, CPS Proxy Folder
    # CPS Folder
    pr("Verifying portal types")
    ttool = portal.portal_types
    ptypes = {
        'CPSCore':('CPS Proxy Document',
                   'CPS Proxy Folder',
                   ),
        'CPSDefault':('Folder',
                      'Dummy',
                      'Text Box',
                      'Tree Box',                      
                      )
        }
    allowed_content_type = {
                            'Section' : ('Section',),
                            'Workspace' : ('Workspace', 'Dummy'),
                            }
    
    ptypes_installed = ttool.objectIds()
    # remove all ptypes
    ttool.manage_delObjects(ptypes_installed)
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
    ttool.manage_addTypeInformation(
        id='Section',
        add_meta_type='Factory-based Type Information',
        typeinfo_name='CPSDefault: Folder',
        )
    ttool['Section'].manage_changeProperties(None,
                                             title='Section',
                                             content_meta_type='Section')
    ttool.manage_addTypeInformation(
        id='Workspace',
        add_meta_type='Factory-based Type Information',
        typeinfo_name='CPSDefault: Folder',
        )
    ttool['Workspace'].manage_changeProperties(None,
                                               title='Workspace',
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
    pr("Verifying roots: %s and %s" % (sections_id, workspaces_id))
    if not portalhas(workspaces_id):
        portal.portal_workflow.invokeFactoryFor(portal.this(), 'Workspace',
                                                workspaces_id)
        portal[workspaces_id].getContent().setTitle('Root of Workspaces') # XXX L10N
        portal[workspaces_id].reindexObject()
        pr("  Adding %s Folder" % workspaces_id)
    if not portalhas(sections_id):
        portal.portal_workflow.invokeFactoryFor(portal.this(), 'Section',
                                                sections_id)
        portal[sections_id].getContent().setTitle('Root of Sections') # XXX L10N        
        portal[sections_id].reindexObject()
        pr("  Adding %s Folder" % sections_id)


    pr("Verifying permissions")
    sections_perm = {
        'Request review':['Manager', 'WorkspaceManager', 'WorkspaceMember', 'SectionReviewer', 'SectionManager'],
        'Review portal content':['Manager', 'SectionReviewer', 'SectionManager'],
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
                       'Add portal content': ['Manager', 'WorkspaceManager', 'WorkspaceMember'],
                       'Add portal folders': ['Manager', 'WorkspaceManager'],
                       'Change permissions': ['Manager', 'WorkspaceManager'],
                       'Delete objects': ['Manager', 'WorkspaceManager', 'WorkspaceMember'],
                       'List folder contents': ['Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'],
                       'Modify portal content': ['Manager', 'WorkspaceManager', 'WorkspaceMember'],
                       'View': ['Manager', 'WorkspaceManager', 'WorkspaceMember', 'WorkspaceReader'],
                       'View management screens': ['Manager', 'WorkspaceManager', 'WorkspaceMember'],
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
        trtool[sections_id].manage_changeProperties(title=sections_id+' Cache', 
                                                    root=sections_id, 
                                                    type_names=('Section',))
        trtool[sections_id].manage_rebuild()
        
    if workspaces_id not in trtool.objectIds():
        pr("  Adding cache for tree %s" % workspaces_id)
        trtool.manage_addCPSTreeCache(id=workspaces_id)
        trtool[workspaces_id].manage_changeProperties(title=workspaces_id+' Cache', 
                                                      root=workspaces_id, 
                                                      type_names=('Workspace',))
        trtool[workspaces_id].manage_rebuild()
        
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
            name='Status History',
            action='string: ${object/absolute_url}/content_status_history',
            condition='python: folder is not object',
            permission='View',
            category='workflow')
        pr(" Added")
    else:
        pr(" Present")

        
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
