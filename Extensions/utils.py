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

from AccessControl import Unauthorized

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission

from Products.CPSDefault.utils import reorderContainterContents

LOG_KEY = 'CPSDefault.utils'


def reorderContainerContents(self, REQUEST):
    """Physically reorder the contents of a container.

    The following paramaters needs to be set in the REQUEST.

    container : the rpath of an object such as a workspace or a section proxy.

    key : to specify on what criteria to do the reordering, usually one uses
    key='id' or key='effective_date'.

    ascending : to specify if the content should be ordered in ascending
    order or descending order.

    Use it for example like this:
    http://localhost/cps/reorderContainerContents?container=sections&key=effective_date&ascending=True
    """
    utool = getToolByName(self, 'portal_url')
    portal = utool.getPortalObject()
    if not _checkPermission(ManagePortal, portal):
        raise Unauthorized("You need the ManagePortal permission.")

    res = []
    container_rpath = REQUEST.form.get('container')
    key = REQUEST.form.get('key')
    ascending = REQUEST.form.get('ascending')
    ascending = ascending == 'True'

    container = self.restrictedTraverse(container_rpath)
    reorderContainterContents(container, key, ascending)

    res.append("Container \"%s\", ascending = %s, reordering done."
               % (container_rpath, ascending))
    return '\n'.join(res)

