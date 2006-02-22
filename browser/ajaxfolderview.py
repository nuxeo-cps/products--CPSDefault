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
from OFS.CopySupport import CopyError
from Products.Five import BrowserView

class AjaxFolderView(BrowserView):

    def _removingHeaders(self, element, headers):
        for header in headers:
            if element.startswith(header):
                element = element[len(header):]
        return element

    def _isUrl(self, id):
        return id.startswith('url:')

    def _checkElementMove(self, from_id, to_place):
        proxy_folder = self.context
        # 1/ the user has all rights
        try:
            to_folder = proxy_folder.restrictedTraverse(to_place)
        except Unauthorized:
            return False

        # 2/ not reflective
        if to_folder == proxy_folder:
            return False

        # 3/ the target container can hold the object
        element_type = proxy_folder[from_id].getContent().portal_type
        allowed_types = [factory.id
                         for factory in to_folder.allowedContentTypes()]
        if element_type not in allowed_types:
            return False

        # 5/ XXX ugly hack
        # at this time we don't want to let the user
        # mess around with folders in the workspace
        # member area, it's too easy to do and dangerous
        if element_type == 'Workspace':
            url = proxy_folder[from_id].absolute_url().lower()
            if url.find('workspaces/members') != -1:
                return False

        return True

    def _checkPositionChange(self, from_id, to_id):
        return from_id != to_id

    def moveElement(self, from_id, to_id):
        """ moving elements from a dragdrop action

        XXX Next version will send json friendly results
        """
        headers = ('draggable', 'droppable', 'droppable-in')
        from_id = self._removingHeaders(from_id, headers)
        proxy_folder = self.context

        if self._isUrl(to_id):
            # checking if all conditions are met
            to_id = to_id[4:].replace('.', '/')

            if not self._checkElementMove(from_id, to_id):
                return ''

            # moving object to another container
            to_folder = proxy_folder.restrictedTraverse(to_id)
            try:
                cb_data = proxy_folder.manage_CPScutObjects([from_id])
                to_folder.manage_CPSpasteObjects(cb_data)
            except CopyError:
                return ''
        else:
            # checking if all conditions are met
            if not self._checkPositionChange(from_id, to_id):
                return '_'

            # changing indexes in order to always
            # position the dragged element *after*
            # the dropped one
            to_id = self._removingHeaders(to_id, headers)
            to_position = proxy_folder.getObjectPosition(to_id)
            from_position = proxy_folder.getObjectPosition(from_id)

            if from_position > to_position:
                to_position += 1
            if from_position == to_position:
                return '_'

            # moving object's position
            proxy_folder.moveObjectToPosition(from_id, to_position)

        if proxy_folder.objectIds() == []:
            return ':'

        return ':'.join([id for id in proxy_folder.objectIds()
                         if not id.startswith('.')])
