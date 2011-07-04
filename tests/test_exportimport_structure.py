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

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

from Products.CPSCore.interfaces import ICPSProxy
from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION
from Products.CMFCore.utils import getToolByName
from Products.CPSCore.interfaces import ICPSSite

class TestImportStructure(CPSTestCase):

    def afterSetUp(self):
        CPSTestCase.afterSetUp(self)

        profile_registry.registerProfile(
            'tests_exportimport',
            'CPS Default import structure Tests',
            "Tests Structure",
            'tests/profiles/exportimport',
            'CPSDefault',
            EXTENSION,
            for_=ICPSSite)

        self.login('manager')

    def assertTraverse(self, container, path):
        obj = container
        for segment in path.split('/'):
            self.assertTrue(obj.hasObject(segment))
            obj = getattr(obj, segment)
        return obj

    def test_import_structure(self):
        stool = self.portal.portal_setup
        stool.setImportContext('profile-CPSDefault:tests_exportimport')
        stool.runImportStep('structure')

        # first level
        sections = self.portal.sections
        ptl = self.assertTraverse(sections, '.cps_portlets/breadcrumb')
        self.assertEquals(ptl.slot, 'fil_ariane')

        # deep within created folders
        ptl = self.assertTraverse(sections,
                                  'some_sub/current/.cps_portlets/mynav')
        self.assertEquals(ptl.slot, 'dans_rubrique')

        # problem with space in object id : xml file is portlet_liens_utiles.xml
        # but does not correspond to the object id (portlet_liens utiles)
        ptl = self.assertTraverse(sections,
                                  '.cps_portlets/portlet_liens utiles')
        self.assertEquals(ptl.slot, 'liens') # breaks if xml file ignored

    def beforeTearDown(self):
        pass # no unregisterProfile API


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestImportStructure))
    return suite
