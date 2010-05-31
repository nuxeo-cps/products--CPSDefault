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

from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFCore.utils import UniqueObject, SimpleItemWithProperties
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from DateTime.DateTime import DateTime

class InformationMessageTool(UniqueObject, SimpleItemWithProperties,
                             ActionProviderBase):
    id = 'portal_information_message'

    security = ClassSecurityInfo()

    _properties = (
    {'id': 'activated', 'type': 'boolean', 'mode': 'w',
     'label': 'Activated'},
    {'id': 'subject', 'type': 'string', 'mode': 'w',
     'label': 'Subject'},
    {'id': 'date', 'type': 'date', 'mode': 'w',
     'label': 'Date'},
    {'id': 'duration', 'type': 'string', 'mode': 'w',
     'label': 'Duration'},
    {'id': 'details', 'type': 'string', 'mode': 'w',
     'label': 'Details'},
    )

    activated = False
    subject = "Undefined subject for now"
    date = DateTime()
    duration = "Undefined duration for now"
    details = "Undefined details for now"

    manage_options = (SimpleItemWithProperties.manage_options +
                      ActionProviderBase.manage_options)

    logger = getLogger(id)

    security.declareProtected(View, 'check')
    def check(self, REQUEST=None):
        """Returns the date (as the number of milliseconds since the Epoch)
        of the information message if it is activated, None otherwise."""
        if self.activated:
            return self.date.millis()
        else:
            return None

    security.declareProtected(ManagePortal, 'config')
    def config(self, properties, REQUEST=None):
        """."""
        self.manage_changeProperties(properties)

InitializeClass(InformationMessageTool)
