# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
# G. Racinet <georges@racinet.fr>
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

from Products.CPSUtil.testing.genericsetup import TestXMLAdapter
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.interfaces import IBody
from Products.CPSDefault.exportimport.proxy import ProxyXMLAdapter

from Products.CPSCore.interfaces import ICPSProxy

class TestExportImportProxy(CPSTestCase, TestXMLAdapter):

    def afterSetUp(self):
        CPSTestCase.afterSetUp(self)
        TestXMLAdapter.setUp(self)
        self.environ.getSite = lambda : self.portal
        self.setPurge(False)
        self.login('manager')

    def zcmlSetUp(self):
        # we don't test CPSDefault's zcml config, but rather force our adapter
        from zope.component import provideAdapter
        provideAdapter(factory=ProxyXMLAdapter,
                       adapts=[ICPSProxy, ISetupEnviron],
                       provides=IBody)

    def buildObject(self):
        return self.portal.workspaces

    def test_proxy_inits(self):
        ws = self.portal.workspaces
        self.importString('<?xml version="1.0"?>'
                          ' <object name="workspaces">'
                          '  <proxy name="subws" portal_type="Workspace"/>'
                          '  <proxy name="file" portal_type="File"/>'
                          ' </object>')
        self.assertTrue(ws.hasObject('file'))
        self.assertEquals(ws.file.portal_type, 'File')
        self.assertTrue(ws.hasObject('subws'))
        self.assertEquals(ws.subws.portal_type, 'Workspace')

    def test_missing_ptype(self):
        self.assertRaises(ValueError, self.importString,
                          '<?xml version="1.0"?>'
                          ' <object name="workspaces">'
                          '  <proxy name="oops"/>'
                          ' </object>')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestExportImportProxy))
    return suite
