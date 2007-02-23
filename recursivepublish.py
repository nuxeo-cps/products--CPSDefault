# (C) Copyright 2007 Nuxeo SAS <http://nuxeo.com>
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
"""Module dedicated to recursive publishing.
"""

import os.path

from zLOG import LOG, DEBUG
from AccessControl import Unauthorized
from AccessControl import ModuleSecurityInfo

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission

LOG_KEY = 'recursivepublish'

WORKSPACE_PORTAL_TYPE = 'Workspace'
SECTION_PORTAL_TYPE = 'Section'

FOLDERISH_PROXY_TYPES = ['folder', 'folderishdocument',
                         'btreefolder', 'btreefolderishdocument']

# XXX : Why couldn't this be protected like this ?
# If so, this gives the following error :
# import of "recursivePublish" from "Products.CPSDefault.recursivepublish" is unauthorized. You are not allowed to access 'recursivePublish' in this context
#security = ModuleSecurityInfo('Products.CPSDefault.recursivepublish')
#security.declareProtected(ManagePortal, 'recursivePublish')
ModuleSecurityInfo('Products.CPSDefault.recursivepublish').declarePublic('recursivePublish')
def recursivePublish(workspace, context):
    """Recursively publish all the content below the given workspace container.
    """
    log_key = LOG_KEY + '.recursivePublish'
    LOG(log_key, DEBUG, "...")
    ttool = getToolByName(context, 'portal_types')
    wtool = getToolByName(context, 'portal_workflow')
    utool = getToolByName(context, 'portal_url')
    portal = utool.getPortalObject()
    if not _checkPermission(ManagePortal, portal):
        raise Unauthorized("You need the ManagePortal permission.")
    workspace_rpath = utool.getRpath(workspace)
    LOG(log_key, DEBUG, "workspace_rpath = %s" % workspace_rpath)

    # This is the rpath independant from either workspace or section
    independant_rpath = '/'.join(workspace_rpath.split('/')[1:])
    LOG(log_key, DEBUG, "independant_rpath = %s" % independant_rpath)

    target_section_rpath = 'sections'
    if independant_rpath:
        target_section_rpath = os.path.join(target_section_rpath, independant_rpath)
    LOG(log_key, DEBUG, "target_section_rpath = %s" % target_section_rpath)
    section_id = '/'.join(target_section_rpath.split('/')[-1:])

    target_section_parent_rpath = '/'.join(target_section_rpath.split('/')[:-1])
    LOG(log_key, DEBUG, "target_section_parent_rpath = %s"
        % target_section_parent_rpath)
    target_section_parent = portal.restrictedTraverse(
        target_section_parent_rpath)
    LOG(log_key, DEBUG, "target_section_parent = %s" % target_section_parent)

    # Creating the target section if it doesn't exist yet
    if not portal.restrictedTraverse(target_section_rpath, None):
        target_section_parent.invokeFactory(type_name=SECTION_PORTAL_TYPE,
                                            id=section_id,
                                            )

    # Setting target section title and description after the target section has
    # been created thus possibly synchronizing through modification already
    # created sections.
    target_section = getattr(target_section_parent, section_id)
    target_section_doc = target_section.getEditableContent()
    # We don't want to change the title and description of the root section,
    # which is the case when independant_rpath is empty.
    if independant_rpath != '':
        workspace_doc = workspace.getContent()
        target_section_doc.edit(Title=workspace_doc.Title(),
                                Description=workspace_doc.Description(),
                                )

    for item_id, item in workspace.objectItems():
        #LOG(log_key, DEBUG, "item_id = %s ..." % item_id)
        if item_id.startswith('.'):
            continue
        fti = ttool[item.portal_type]
        if fti.cps_proxy_type in FOLDERISH_PROXY_TYPES:
            recursivePublish(workspace=item, context=context)
        else:
            LOG(log_key, DEBUG,
                "Publishing the document %s in the right section ..." % item_id)
            workflow_action = 'copy_submit'
            transition = 'publish'
            comments = 'Automatic recursive publishing.'
            wtool.doActionFor(item, workflow_action,
                              dest_container=target_section_rpath,
                              initial_transition=transition,
                              comment=comments)
            LOG(log_key, DEBUG,
                "Publishing the document %s in the right section DONE" % item_id)
