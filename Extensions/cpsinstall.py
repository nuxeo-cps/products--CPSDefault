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

zexpdir = os.path.join('Products', 'NuxCPS3')

def tryimport(container, name, suffix='zexp', zexpdir=zexpdir, pr=None):
    zexppath = getPath(zexpdir, name, suffixes=(suffix, ))
    if zexppath is None:
        pr(" !!! Unable to find %s.%s in %s" % (name, suffix, zexpdir))
    else:
        container._importObjectFromFile(zexppath)
        pr(" Import of %s.%s" % (name, suffix))


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
    for role in ('Reader', 'Reviewer', 'Worker', 'SectionManager'):
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

    # create index_html for portal redirection
    pr("Verifying global index_html")
    #if portalhas('index_html'):
        #if portal.index_html.meta_type != 'DTML Method':
            #pr(" !!! index_html is not a DTML Method")
            #primp()
        #else:
            #prok()
    #else:
        #pr(" Creating index_html")
        #portal.manage_addProduct['OFSP'].manage_addDTMLMethod('index_html')
        #doc = portal['index_html']
        #doc.munge('<dtml-var portal>')

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
            action='proxies',
            meta_type='*',
            event_type='synchronous',
            notification_type='*',
            compressed=0)
    if 'portal_trees' in subscribers:
        prok()
    else:
        pr(" Creation portal_proxies subscribers")
        portal.portal_eventservice.manage_addSubscriber(
            subscriber='portal_trees',
            action='tree',
            meta_type='*',
            event_type='synchronous',
            notification_type='*',
            compressed=0)


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


    # import the 4 standard workflow
    pr("Setup workflow shemas")
    wftool = portal.portal_workflow
    wfids = wftool.objectIds()
    for wfid in ('cps_section_document_workflow',
                 'cps_section_workflow',
                 'cps_workspace_document_workflow',
                 'cps_workspace_workflow'):
        if wfid in wfids:
            wftool.manage_delObjects([wfid])
        tryimport(wftool, wfid, pr=pr)

    #pr("Verifying new actions")
    #actionadd = {
                 #'portal_actions':[
                                   #ActionInformation(id='print',
                                                     #title='_action_print_',
                                                     #action=Expression(
                                                                       #text='string:${object_url}/view?pp=1'),
                                                      #text='string:${portal_url}/Members/'),
                                    #permissions=('Manage users',),
                                    #category='global',
                                    #visible=1),
                 #],
    #}
    #for tool, newactions in actionadd.items():
        #actions = list(portal[tool]._actions)
        #for action in newactions:
            #if action.id not in [ac.id for ac in actions]:
                #actions.append(action)
                #pr(" Add %s: %s" % (tool, action.id))
        #portal[tool]._actions = actions
        
        
    # setup portal_type: CPS Proxy Document, CPS Proxy Folder, 
    # CPS Dummy Document, CPS Folder
    pr("Verifying portal types")
    ttool = portal.portal_types
    ptypes = {
        'NuxCPS3':('CPS Proxy Document',
                   'CPS Proxy Folder',
#                   'CPS Proxy Folderish Document',
                   'CPS Folder',
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
        'Section': 'cps_section_workflow',
        'Workspace': 'cps_workspace_workflow',
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
        pr("  Adding %s Folder" % workspaces_id)
    if not portalhas(sections_id):
        portal.portal_workflow.invokeFactoryFor(portal.this(), 'Section',
                                                sections_id)
        pr("  Adding %s Folder" % sections_id)
    
    pr("Verifying local workflow association")
    if not '.cps_workflow_configuration' in portal[workspaces_id].objectIds():
        pr("  Adding workflow configuration to %s" % workspaces_id)
        portal[workspaces_id].manage_addProduct['NuxCPS3'].addCPSWorkflowConfiguration()
        wfc = getattr(portal[workspaces_id], '.cps_workflow_configuration')
        wfc.manage_addChain(portal_type='Workspace',
                            chain='cps_workspace_workflow')
        wfc.manage_addChain(portal_type='Section',
                            chain='')
        wfc.manage_addChain(portal_type='Dummy',
                            chain='cps_workspace_document_workflow',
                            under_sub_add=1)
        
    if not '.cps_workflow_configuration' in portal[sections_id].objectIds():
        pr("  Adding workflow configuration to %s" % sections_id)
        portal[sections_id].manage_addProduct['NuxCPS3'].addCPSWorkflowConfiguration()
        wfc = getattr(portal[sections_id], '.cps_workflow_configuration')
        wfc.manage_addChain(portal_type='Workspace',
                            chain='')
        wfc.manage_addChain(portal_type='Section',
                            chain='cps_section_workflow')
        wfc.manage_addChain(portal_type='Dummy',
                            chain='cps_section_document_workflow',
                            under_sub_add=1)
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
