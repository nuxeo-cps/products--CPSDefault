# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
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
  EventCalendarBox
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Acquisition import aq_base
from OFS.Image import File
from OFS.Folder import Folder
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from BaseBox import BaseBox

from zLOG import LOG, DEBUG

factory_type_information = (
    {'id': 'Event Calendar Box',
     'title': 'portal_type_EventCalendarBox_title',
     'description': 'portal_type_EventCalendarBox_description',
     'meta_type': 'Event Calendar Box',
     'icon': 'box.gif',
     'product': 'CPSDefault',
     'factory': 'addEventCalendarBox',
     'immediate_view': 'eventcalendarbox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'eventcalendarbox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class EventCalendarBox(BaseBox):
    """
    A box displaying Event Calendar objects (CPS patched version of CMFCalendar).
    """
    meta_type = 'Event Calendar Box'
    portal_type = 'Event Calendar Box'

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id': 'events_in', 'type': 'text', 'mode': 'w', 
         'label': 'location of events to be shown'},
        )

    events_in = None
    event_types = []

    def __init__(self, id, flash_filename='', **kw):
        BaseBox.__init__(self, id, category='eventcalendarbox', kw=kw)

    def edit(self, **kw):
        self.events_in = self.REQUEST.form.get('events_in')
        if not self.events_in:
            self.events_in = None
        self.event_types = self.REQUEST.form.get('event_types')
        if not self.event_types:
            #necessary as the edit form does an inclusion test and
            #thus needs event_types to be a sequence, even if empty
            self.event_types = []
        BaseBox.edit(self, **kw)


InitializeClass(EventCalendarBox)


def addEventCalendarBox(dispatcher, id, REQUEST=None, **kw):
    """Add an Event Calendar Box."""
    ob = EventCalendarBox(id, **kw)
    dispatcher._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
