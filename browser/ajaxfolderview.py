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
from Products.Five import BrowserView

class AjaxFolderView(BrowserView):

    def _removingHeaders(self, element, headers):
        for header in headers:
            if element.startswith(header):
                element = element[len(header):]
        return element

    def _isUrl(self, id):
        return id.find('/') != -1

    def moveElement(self, from_id, to_id):
        """ moving elements from a dragdrop action """
        headers = ('draggable', 'droppable')
        from_id = self._removingHeaders(from_id, headers)
        proxy_folder = self.context

        if self._isUrl(to_id):
            # moving object to another container
            to_folder = proxy_folder.restrictedTraverse(to_id)
            cb_data = proxy_folder.manage_cutObjects([from_id])
            to_folder.manage_pasteObjects(cb_data)
        else:
            # moving object's position
            to_id = self._removingHeaders(to_id, headers)
            if from_id == to_id:
                return ''
            to_position = proxy_folder.getObjectPosition(to_id)
            proxy_folder.moveObjectToPosition(from_id, to_position)

        return ':'.join([id for id in proxy_folder.objectIds()
                         if not id.startswith('.')])
