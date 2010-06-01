# (C) Copyright 2010 AFUL <http://aful.org/>
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

import unittest
from DateTime.DateTime import DateTime

from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSDefault.tests.CPSTestCase import MANAGER_ID

class TestInformationMessageTool(CPSTestCase):
    login_id = MANAGER_ID

    def afterSetUp(self):
        self.login(self.login_id)
        self.infotool = self.portal.portal_information_message

    def beforeTearDown(self):
        self.logout()

    def test_config(self):
        subject = "New subject"
        before = DateTime()
        self.infotool.config({ 'subject': subject })
        self.assertEqual(subject, self.infotool.subject)
        self.assertNotEqual(before, self.infotool.last_modified)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInformationMessageTool))
    return suite

