# (C) Copyright 2010 AFUL <http://aful.org/>
# Author: M.-A. Darche
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

from logging import getLogger

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder

from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFCore.utils import UniqueObject

class InformationMessageTool(UniqueObject, Folder):
    id = 'portal_information_message'
    meta_type = 'InformationMessage Tool'

    security = ClassSecurityInfo()

    security.declareProtected(View, 'fetch')
    def fetch(self, REQUEST=None):
        """Fecthes an information message if there is one."""
        return "This is the message!"

InitializeClass(InformationMessageTool)
