# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
"""
    here we go
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
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent


from Products.NuxCPS3.CPSWorkflow import TRANSITION_INITIAL_CREATE, \
     TRANSITION_ALLOWSUB_CREATE, \
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
    skins = ('sss3', 'sss3_images', 'nuxcps3', )
    paths = {
        'sss3': 'Products/SSS3/skins',
        'sss3_images': 'Products/SSS3/skins/images',
        'nuxcps3': 'Products/NuxCPS3/skins',
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


    # add tools (CPS Tools): CPS Event Service Tool, CPS Proxies Tool,
    # CPS Object Repository, Tree tools
    pr("Verifying CPS Tools")
    if portalhas('portal_eventservice'):
        prok()
    else:
        pr(" Creating portal_eventservice")
        portal.manage_addProduct["NuxCPS3"].manage_addTool(
            'CPS Event Service Tool')
    if portalhas('portal_proxies'):
        prok()
    else:
        pr(" Creating portal_proxies")
        portal.manage_addProduct["NuxCPS3"].manage_addTool('CPS Proxies Tool')
    if portalhas('portal_repository'):
        prok()
    else:
        pr(" Creating portal_repository")
        portal.manage_addProduct["NuxCPS3"].manage_addTool(
            'CPS Repository Tool')

    if portalhas('portal_trees'):
        prok()
    else:
        pr(" Creating (CPS Tools) CPS Trees Tool")
        portal.manage_addProduct["NuxCPS3"].manage_addTool('CPS Trees Tool')
    
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
        portal.manage_addProduct["NuxCPS3"].manage_addTool('CPS Workflow Tool')


    # create workflow
    pr("Setup workflow shemas")
    wftool = portal.portal_workflow
    wfids = wftool.objectIds()

    # WF workspace
    wfid = 'wf_workspace'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    
    for s in ('work', ):
        wf.states.addState(s)
    for t in ('creation', 'create_subobject'):
        wf.transitions.addTransition(t)

    # wf.states.setInitialState('work')
    s = wf.states.get('work')
    s.setProperties(title='Work', 
                    transitions=('create_subobject',))
    t = wf.transitions.get('creation')
    t.setProperties(title='Creation', new_state_id='work', 
                    transition_behavior=(TRANSITION_INITIAL_CREATE, ), 
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='workflow', actbox_url='',
                    props={'guard_permissions':'', 'guard_roles':'', 'guard_expr':''},
                    )
    t = wf.transitions.get('create_subobject')
    t.setProperties(title='Create a sub object', new_state_id='', 
                    transition_behavior=(TRANSITION_ALLOWSUB_CREATE, ), 
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION, 
                    actbox_name='Create sub workspace', actbox_category='workflow',
                    actbox_url='%(content_url)s/workspace_create_form',
                    props={'guard_permissions':'', 'guard_roles':'WorkspaceManager; Manager', 'guard_expr':''},
                    )

    # WF workspace document
    wfid = 'wf_workspace_document'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    
    for s in ('work', ):
        wf.states.addState(s)
    for t in ('creation', 'publish', ):
        wf.transitions.addTransition(t)
    for p in (View, ModifyPortalContent, ):
        wf.addManagedPermission(p)
        
    # wf.states.setInitialState('work')
    s = wf.states.get('work')
    s.setProperties(title='Work', 
                    transitions=('publish',))
    s.setPermission(ModifyPortalContent, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember'))
    s.setPermission(View, 0, ('Manager', 'WorkspaceManager', 'WorkspaceMember'))

    t = wf.transitions.get('creation')
    t.setProperties(title='Creation', new_state_id='work', 
                    transition_behavior=(TRANSITION_INITIAL_CREATE, ),
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='workflow', actbox_url='',
                    props={'guard_permissions':'', 'guard_roles':'', 'guard_expr':''},
                    )
    t = wf.transitions.get('publish')
    t.setProperties(title='Publish', new_state_id='', 
                    transition_behavior=(TRANSITION_BEHAVIOR_PUBLISHING, ), 
                    clone_allowed_transitions=('in_submit', 'in_publish'),
                    trigger_type=TRIGGER_USER_ACTION, 
                    actbox_name='Publish', actbox_category='workflow',
                    actbox_url='%(content_url)s/content_publish_form',
                    props={'guard_permissions':'', 
                           'guard_roles':'WorkspaceMember; WorkspaceManager; Manager', 
                           'guard_expr':''},
                    )

    # WF section
    wfid = 'wf_section'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    
    for s in ('work', ):
        wf.states.addState(s)
    for t in ('creation', 'create_subobject'):
        wf.transitions.addTransition(t)

    s = wf.states.get('work')
    s.setProperties(title='Work', 
                    transitions=('create_subobject',))
    t = wf.transitions.get('creation')
    t.setProperties(title='Creation', new_state_id='work', 
                    transition_behavior=(TRANSITION_INITIAL_CREATE, ), 
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='workflow', actbox_url='',
                    props={'guard_permissions':'', 'guard_roles':'', 'guard_expr':''},
                    )
    t = wf.transitions.get('create_subobject')
    t.setProperties(title='Create a sub object', new_state_id='', 
                    transition_behavior=(TRANSITION_ALLOWSUB_CREATE, ), 
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION, 
                    actbox_name='Create sub section', actbox_category='workflow',
                    actbox_url='%(content_url)s/section_create_form',
                    props={'guard_permissions':'', 'guard_roles':'SectionManager; Manager', 'guard_expr':''},
                    )

    # WF section document
    wfid = 'wf_section_document'
    pr(" Setup workflow %s" % wfid)
    if wfid in wfids:
        wftool.manage_delObjects([wfid])
    wftool.manage_addWorkflow(id=wfid,
                              workflow_type='cps_workflow (Web-configurable workflow for CPS)')
    wf = wftool[wfid]
    
    for s in ('pending', 'published' ):
        wf.states.addState(s)
    for t in ('in_publish', 'in_submit', 'publish', 'unpublish', ):
        wf.transitions.addTransition(t)
    for p in (View, ModifyPortalContent, ):
        wf.addManagedPermission(p)
        
    s = wf.states.get('pending')
    s.setProperties(title='Waiting for reviewer', 
                    transitions=('publish',))
    s.setPermission(ModifyPortalContent, 0, ('Manager', ))
    s.setPermission(View, 0, ('SectionReviewer', 'SectionManager', 'Manager'))
    s = wf.states.get('published')
    s.setProperties(title='Public', 
                    transitions=('depublish',))
    s.setPermission(ModifyPortalContent, 0, ('Manager', ))
    s.setPermission(View, 0, ('SectionReader', 'SectionReviewer', 'SectionManager', 'Manager'))
    
    t = wf.transitions.get('in_publish')
    t.setProperties(title='Member publishes directly', new_state_id='published', 
                    transition_behavior=(TRANSITION_INITIAL_CREATE, TRANSITION_BEHAVIOR_FREEZE,),
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='', actbox_url='',
                    props={'guard_permissions':'', 
                           'guard_roles':'SectionReviewer; SectionManager; Manager', 
                           'guard_expr':''},
                    )
    t = wf.transitions.get('in_submit')
    t.setProperties(title='Member requests publishing', new_state_id='pending', 
                    transition_behavior=(TRANSITION_INITIAL_CREATE, TRANSITION_BEHAVIOR_FREEZE), 
                    clone_allowed_transitions=None,
                    actbox_name='', actbox_category='', actbox_url='',
                    props={'guard_permissions': '', 
                           'guard_roles': '', 
                           'guard_expr': ''},
                    )
    t = wf.transitions.get('publish')
    t.setProperties(title='Member requests publishing', new_state_id='published', 
                    transition_behavior=None,
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION, 
                    actbox_name='Publish', actbox_category='workflow', 
                    actbox_url='%(content_url)s/content_publish_form',
                    props={'guard_permissions':'', 
                           'guard_roles':'SectionReviewer; SectionManager, Manager', 
                           'guard_expr':''},
                    )
    t = wf.transitions.get('unpublish')
    t.setProperties(title='remove the doc from publication', new_state_id='pending', 
                    transition_behavior=None,
                    clone_allowed_transitions=None,
                    trigger_type=TRIGGER_USER_ACTION, 
                    actbox_name='Un Publish', actbox_category='workflow', 
                    actbox_url='%(content_url)s/content_unpublish_form',
                    props={'guard_permissions':'', 
                           'guard_roles':'SectionReviewer; SectionManager, Manager', 'guard_expr':''},
                    )
   
        
    # setup portal_type: CPS Proxy Document, CPS Proxy Folder, 
    # CPS Dummy Document, CPS Folder
    pr("Verifying portal types")
    ttool = portal.portal_types
    ptypes = {
        'NuxCPS3':('CPS Proxy Document',
                   'CPS Proxy Folder',
                   ),
        'SSS3':('Dummy',)
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
        typeinfo_name='NuxCPS3: CPS Folder',
        )
    ttool['Section'].manage_changeProperties(None,
                                             title='Section',
                                             content_meta_type='Section')
    ttool.manage_addTypeInformation(
        id='Workspace',
        add_meta_type='Factory-based Type Information',
        typeinfo_name='NuxCPS3: CPS Folder',
        )
    ttool['Workspace'].manage_changeProperties(None,
                                               title='Workspace',
                                               content_meta_type='Workspace')

    # check workflow association
    pr("Verifying workflow schemas")
    wfs = {
        'Section': 'wf_section',
        'Workspace': 'wf_workspace',
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
        portal.workspaces.getContent().setTitle('Workspaces Root') # XXX L10N        
        portal.workspaces.reindexObject()
        pr("  Adding %s Folder" % workspaces_id)
    if not portalhas(sections_id):
        portal.portal_workflow.invokeFactoryFor(portal.this(), 'Section',
                                                sections_id)
        portal.workspaces.getContent().setTitle('Sections Root') # XXX L10N        
        portal.workspaces.reindexObject()
        pr("  Adding %s Folder" % sections_id)



   
    
    pr("Verifying local workflow association")
    if not '.cps_workflow_configuration' in portal[workspaces_id].objectIds():
        pr("  Adding workflow configuration to %s" % workspaces_id)
        portal[workspaces_id].manage_addProduct['NuxCPS3'].addCPSWorkflowConfiguration()
        wfc = getattr(portal[workspaces_id], '.cps_workflow_configuration')
        wfc.manage_addChain(portal_type='Workspace',
                            chain='wf_workspace')
        wfc.manage_addChain(portal_type='Section',
                            chain='')
        wfc.manage_addChain(portal_type='Dummy',
                            chain='wf_workspace_document')
        
    if not '.cps_workflow_configuration' in portal[sections_id].objectIds():
        pr("  Adding workflow configuration to %s" % sections_id)
        portal[sections_id].manage_addProduct['NuxCPS3'].addCPSWorkflowConfiguration()
        wfc = getattr(portal[sections_id], '.cps_workflow_configuration')
        wfc.manage_addChain(portal_type='Workspace',
                            chain='')
        wfc.manage_addChain(portal_type='Section',
                            chain='wf_section')
        wfc.manage_addChain(portal_type='Dummy',
                            chain='wf_section_document')
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
