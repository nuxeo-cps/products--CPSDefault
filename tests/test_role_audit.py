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

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSDefault.tests.CPSTestCase import MANAGER_ID

from Products.CPSUtil.tests.web_conformance import assertValidXhtml

from Products.CPSDefault.browser.roles import RoleView

class TestRoleAudit(CPSTestCase):

    login_id = MANAGER_ID

    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()

    def beforeTearDown(self):
        self.logout()

    def testViewClass(self):
        request = None
        role_view = RoleView(self.portal.sections, request)
        rendering = role_view.synthesis()
        self.assert_(rendering)

    def testView(self):
        view_id = 'cps_role_audit.html'
        #meth = getattr(self.portal, view_id)
        #rendering = meth()
        #self.assert_(rendering)
        #assertValidXhtml(rendering, view_id)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRoleAudit))
    return suite
