# -*- coding: iso-8859-15 -*-
# (C) Copyright 2006 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
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
"""
    View that knows how to deal with ajax requests
    on folder
"""
from AccessControl import Unauthorized
from Products.Five import BrowserView

class AjaxFolderView(BrowserView):

    def _removingHeaders(self, element, headers):
        for header in headers:
            if element.startswith(header):
                element = element[len(header):]
        return element

    def _isUrl(self, id):
        return id.find('/') != -1

    def _checkElementMove(self, from_id, to_place):
        proxy_folder = self.context
        # 1/ the user has all rights
        try:
            to_folder = proxy_folder.restrictedTraverse(to_place)
        except Unauthorized:
            return False

        # 2/ not reflective
        if to_folder is proxy_folder:
            return False

        # 3/ the target container is not the current one
        # or doesn't have already an object with the same id
        if from_id in to_folder.objectIds():
            return False

        # 4/ the target container can hold the object
        element_type = proxy_folder[from_id].getContent().portal_type
        allowed_types = [factory.id
                         for factory in to_folder.allowedContentTypes()]
        if element_type not in allowed_types:
            return False

        # 5/ TODO: when the user moves documents
        # from workspaces to sections and on the other way
        # we need to change their state here, like what's done
        # in regular copy-cut-paste operations

        # 6/ XXX ugly hack
        # the element is not a member folder or
        # the members folders itself
        url = proxy_folder[from_id].absolute_url().lower()
        if url.endswith('workspaces/members'):
            return False

        url = url.split('/')
        if len(url) > 2:
            return url[-2] != 'members' and url[-3] != 'workspaces'
        else:
            return True

    def _checkPositionChange(self, from_id, to_id):
        return from_id != to_id

    def moveElement(self, from_id, to_id):
        """ moving elements from a dragdrop action """
        headers = ('draggable', 'droppable', 'droppable-in')
        from_id = self._removingHeaders(from_id, headers)
        proxy_folder = self.context

        if self._isUrl(to_id):
            # checking if all conditions are met
            if not self._checkElementMove(from_id, to_id):
                return ''

            # moving object to another container
            to_folder = proxy_folder.restrictedTraverse(to_id)
            cb_data = proxy_folder.manage_cutObjects([from_id])
            to_folder.manage_pasteObjects(cb_data)
        else:
            # checking if all conditions are met
            if not self._checkPositionChange(from_id, to_id):
                return ''

            # moving object's position
            to_id = self._removingHeaders(to_id, headers)
            to_position = proxy_folder.getObjectPosition(to_id)
            proxy_folder.moveObjectToPosition(from_id, to_position)

        return ':'.join([id for id in proxy_folder.objectIds()
                         if not id.startswith('.')])
