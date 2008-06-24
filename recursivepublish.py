# (C) Copyright 2007-2008 Nuxeo SAS <http://nuxeo.com>
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
from logging import getLogger

from AccessControl import Unauthorized
from AccessControl import ModuleSecurityInfo
from AccessControl.requestmethod import postonly

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission

LOG_KEY = 'recursivepublish'

WORKSPACE_PORTAL_TYPE = 'Workspace'
SECTION_PORTAL_TYPE = 'Section'

FOLDERISH_PROXY_TYPES = ['folder', 'folderishdocument',
                         'btreefolder', 'btreefolderishdocument']

security = ModuleSecurityInfo('Products.CPSDefault.recursivepublish')

security.declarePublic('recursivePublish')
@postonly
def recursivePublish(workspace, target_section_rpaths, context, REQUEST=None):
    """Recursively publish all the content below the given workspace container
    into the given target sections.
    """
    logger = getLogger(LOG_KEY + '.recursivePublish')
    logger.debug("target_section_rpaths = %s" % target_section_rpaths)
    utool = getToolByName(context, 'portal_url')
    portal = utool.getPortalObject()
    for rpath in target_section_rpaths:
        recursivePublishInFolder(workspace, rpath, context)
    logger.debug("DONE")


security.declarePrivate('recursivePublishInFolder')
def recursivePublishInFolder(workspace, target_section_rpath, context):
    logger = getLogger(LOG_KEY + '.recursivePublishInFolder')
    utool = getToolByName(context, 'portal_url')
    ttool = getToolByName(context, 'portal_types')
    wtool = getToolByName(context, 'portal_workflow')
    portal = utool.getPortalObject()

    target_section = portal.restrictedTraverse(target_section_rpath, None)
    if target_section is None:
        raise ValueError("Folder %s doesn't exist." % target_section_rpath)

    for item_id, item in workspace.objectItems():
        logger.debug("item = %s ..." % utool.getRpath(item))

        # Don't publish special items such as configuration files
        if item_id.startswith('.'):
            continue

        # Don't publish documents which are locked or being worked on,
        # since they can't be published.
        proxy_info = context.getContentInfo(item)
        if proxy_info['review_state'] in ('locked', 'draft'):
            continue

        fti = ttool[item.portal_type]
        if fti.cps_proxy_type not in FOLDERISH_PROXY_TYPES:
            logger.debug("Publishing the document %s in the right section ..."
                         % item_id)
            workflow_action = 'copy_submit'
            transition = 'publish'
            comments = 'Automatic recursive publishing.'
            wtool.doActionFor(item, workflow_action,
                              dest_container=target_section_rpath,
                              initial_transition=transition,
                              comment=comments)
            logger.debug("Publishing the document %s in the right section DONE"
                         % item_id)
        else:
            # Creating the folder if it doesn't exist yet
            target_folder = getattr(target_section, item_id, None)
            if target_folder is None:
                target_section.invokeFactory(type_name=SECTION_PORTAL_TYPE,
                                             id=item_id,
                                             )
                target_folder = getattr(target_section, item_id)
            # Setting target section title and description after the target
            # section has been created thus possibly synchronizing through
            # modification already created sections.
            folder_doc = item.getContent()
            target_folder_doc = target_folder.getEditableContent()
            target_folder_doc.edit(Title=folder_doc.Title(),
                                   Description=folder_doc.Description(),
                                   )

            # Then looping through the recursion
            recursivePublishInFolder(item, utool.getRpath(target_folder),
                                     context)
