# (C) Copyright 2010 AFUL <http://aful.org/>
# Authors:
# M.-A. Darche
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

import unittest
from time import sleep

from DateTime.DateTime import DateTime

from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSDefault.tests.CPSTestCase import MANAGER_ID

from Products.CPSUtil.tests.web_conformance import assertValidXhtml

class TestInformationMessageTool(CPSTestCase):

    login_id = MANAGER_ID

    def afterSetUp(self):
        self.before = DateTime()
        self.login(self.login_id)
        self.infotool = self.portal.portal_information_message

    def beforeTearDown(self):
        self.logout()

    def test_config(self):
        subject = "New subject"
        self.assertEqual(None, self.infotool.last_modified)
        self.assertNotEqual(subject, self.infotool.subject)
        sleep(1)
        self.infotool.config({ 'subject': subject })
        self.assertEqual(subject, self.infotool.subject)
        self.assertNotEqual(self.before, self.infotool.last_modified)

    def test_check_activation(self):
        self.infotool.activated = False
        date = self.infotool.check()
        self.assertEqual(None, date)

    def test_check_instant_display(self):
        modified_date = DateTime()
        self.infotool.activated = True
        self.infotool.last_modified = modified_date
        self.infotool.instant_display = True
        date = self.infotool.check()
        self.assertNotEqual(modified_date, date)

    def test_check_timed_display(self):
        last_modified = DateTime()
        self.infotool.activated = True
        self.infotool.last_modified = last_modified
        self.infotool.instant_display = False

        now = DateTime()

        self.infotool.timed_display_start = now - 10
        self.infotool.timed_display_stop = now + 10
        date = self.infotool.check()
        self.assertNotEqual(None, date)

        self.infotool.timed_display_start = now - 20
        self.infotool.timed_display_stop = now - 10
        date = self.infotool.check()
        self.assertEqual(None, date)

        self.infotool.timed_display_start = now + 10
        self.infotool.timed_display_stop = now + 20
        date = self.infotool.check()
        self.assertEqual(None, date)

    def test_view(self):
        view_id = 'information_message_config_form'
        method = getattr(self.portal, view_id)
        rendering = method()
        self.assert_(rendering)
        assertValidXhtml(rendering, view_id)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInformationMessageTool))
    return suite

