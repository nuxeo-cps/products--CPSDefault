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

from Products.CMFCore.utils import getToolByName

LOG_KEY = 'recursivepublish'

WORKSPACE_PORTAL_TYPE = 'Workspace'
SECTION_PORTAL_TYPE = 'Section'

FOLDERISH_PROXY_TYPES = ['folder', 'folderishdocument',
                         'btreefolder', 'btreefolderishdocument']

def recursivePublish(self, workspace=None, workspace_rpath=None, REQUEST=None):
    """Recursively publish all the content below the given workspace container.

    Example :
    http://mysite.net/workspaces/recursivePublish?rpath=workspaces/folder1
    """
    log_key = LOG_KEY + '.recursivePublish'
    LOG(log_key, DEBUG, "...")

    ttool = getToolByName(self, 'portal_types')
    wtool = getToolByName(self, 'portal_workflow')
    utool = getToolByName(self, 'portal_url')
    portal = utool.getPortalObject()
    if REQUEST is not None:
        workspace_rpath = REQUEST.form.get('rpath')
    if workspace is not None:
        workspace_rpath = utool.getRpath(workspace)
    else:
        workspace = portal.restrictedTraverse(workspace_rpath)
    LOG(log_key, DEBUG, "workspace_rpath = %s" % workspace_rpath)

    # This is the rpath independant from either workspace or section
    independant_rpath = '/'.join(workspace_rpath.split('/')[1:])
    LOG(log_key, DEBUG, "independant_rpath = %s" % independant_rpath)

    target_section_rpath = os.path.join('sections', independant_rpath)
    LOG(log_key, DEBUG, "target_section_rpath = %s" % target_section_rpath)
    target_section_parent_rpath, section_id = os.path.split(target_section_rpath)
    LOG(log_key, DEBUG, "target_section_parent_rpath = %s"
        % target_section_parent_rpath)
    target_section_parent = portal.restrictedTraverse(
        target_section_parent_rpath)

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
    workspace_doc = workspace.getContent()
    target_section_doc.edit(Title=workspace_doc.Title(),
                            Description=workspace_doc.Description(),
                            )

    for item_id, item in workspace.objectItems():
        fti = ttool[item.portal_type]
        if fti.cps_proxy_type in FOLDERISH_PROXY_TYPES:
            self.recursivePublish(workspace=item)
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

    return True
