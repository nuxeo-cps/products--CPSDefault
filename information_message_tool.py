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

    activated = False
    subject = "Undefined subject for now"
    date = "Undefined date for now"
    duration = "Undefined duration for now"
    details = "Undefined details for now"

    security.declareProtected(View, 'check')
    def check(self, REQUEST=None):
        """Returns True if there is an activated information message, nothing otherwise."""
        return self.activated

InitializeClass(InformationMessageTool)
