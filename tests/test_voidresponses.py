# (C) Copyright 2012 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from Products.CMFCore.utils import getToolByName
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

from AccessControl import Unauthorized
from DateTime.DateTime import DateTime
from Products.CPSUtil.http import set_if_modified_since_header
from Products.CPSDefault.voidresponses import ImsResponseHandler

class VoidResponsesTestCase(CPSTestCase):

    def afterSetUp(self):
        """Setup a subsection, and last modified dates for it and the portal.
        """
        sections = self.sections = self.portal.sections
        self.request = self.app.REQUEST
        self.response = self.request.RESPONSE

        self.login('manager')
        wftool = self.wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.invokeFactoryFor(sections, 'Section', 'subs')
        subs = self.subs = sections.subs

        enable_ims = ImsResponseHandler.enableIfModifiedSince
        enable_ims(subs, DateTime('2011/01/01'))
        enable_ims(self.sections, DateTime('2011/06/01'))
        self.logout()

    def test_ims_response(self):
        set_if_modified_since_header(self.request,
                                     'Tue, 1 Mar 2011, 00:00:00 GMT')

        # enabled, and modified after
        handler = ImsResponseHandler(self.sections, self.request)
        self.assertFalse(handler.respond())
        self.failIfEqual(self.response.getStatus(), 304)

        # not enabled
        handler = ImsResponseHandler(self.portal, self.request)
        self.assertFalse(handler.respond())
        self.failIfEqual(self.response.getStatus(), 304)

        # enabled, and modified before
        handler = ImsResponseHandler(self.subs, self.request)
        self.assertTrue(handler.respond())
        self.assertEquals(self.response.getStatus(), 304)

    def test_ims_response_authenticated(self):
        # no 304 response for authenticated sessions
        set_if_modified_since_header(self.request,
                                     'Tue, 1 Mar 2011, 00:00:00 GMT')
        self.login('manager')
        handler = ImsResponseHandler(self.subs, self.request)
        self.assertFalse(handler.respond())
        self.failIfEqual(self.response.getStatus(), 304)

    def test_getLastModificationDate(self):
        get_lmd = ImsResponseHandler.getLastModificationDate
        self.assertEquals(get_lmd(self.portal), None)
        self.assertEquals(get_lmd(self.sections), DateTime('2011/06/01'))

    def test_enable_ims(self):
        enable_ims = ImsResponseHandler.enableIfModifiedSince
        now = DateTime()

        def check(folder):
            enable_ims(folder)
            self.assertTrue(
                ImsResponseHandler.getLastModificationDate(folder) >= now)

        self.login('manager')
        check(self.portal.workspaces) # brand new
        check(self.portal.sections) # already existing

        self.logout()
        self.assertRaises(Unauthorized, check, self.portal.workspaces)

    def test_invalidations(self):
        # publish something inside of sections (must invalidate),
        # but outside of sub-section (musn't)
        get_lmd = ImsResponseHandler.getLastModificationDate
        wftool = self.wftool
        self.login('manager')

        ws = self.portal.workspaces
        wftool.invokeFactoryFor(ws, 'Document', 'doc')
        # sanity check : nothing happening in workspaces should change dates
        self.assertEquals(get_lmd(self.sections), DateTime('2011/06/01'))

        pub_time = DateTime() - 1/86400.0 # tool uses 1 sec safety
        wftool.doActionFor(ws.doc, 'copy_submit', dest_container='sections',
                           initial_transition='publish')

        self.assertEquals(get_lmd(self.subs), DateTime('2011/01/01'))
        self.assertTrue(get_lmd(self.sections) >= pub_time)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(VoidResponsesTestCase),
        ))

