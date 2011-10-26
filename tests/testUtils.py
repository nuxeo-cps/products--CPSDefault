# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
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

import unittest
from Testing.ZopeTestCase import ZopeTestCase

from Products.CPSDefault import utils
from CPSTestCase import CPSTestCase

class TestUtils(ZopeTestCase):

    def test_getNonArchivedVersionContextUrl(self):
        url0 = 'http://toto.com/titi/archivedRevision/123'
        url1 = 'http://toto.com/titi'
        self.assertEquals(utils.getNonArchivedVersionContextUrl(url0), url1)

class IntegrationTestUtils(CPSTestCase):

    def test_manageCPSLanguages_delete_tuple(self):
        # if this changes, the test has to be adapted
        self.assertEquals(set(self.portal.available_languages),
                          set(('fr', 'en', 'de')))
        utils.manageCPSLanguage(self.portal, 'delete', 'en', ('fr', 'de'))
        self.assertEquals(self.portal.available_languages, ('en',))

    def test_manageCPSLanguages_delete_list(self):
        # if this changes, the test has to be adapted
        self.assertEquals(set(self.portal.available_languages),
                          set(('fr', 'en', 'de')))
        # it works with a list, too
        utils.manageCPSLanguage(self.portal, 'delete', 'en', ['fr', 'de'])
        self.assertEquals(self.portal.available_languages, ('en',))

    def test_manageCPSLanguages_delete_str(self):
        # passing a simple string is allowed
        # if this changes, the test has to be adapted
        self.assertEquals(set(self.portal.available_languages),
                          set(('fr', 'en', 'de')))
        utils.manageCPSLanguage(self.portal, 'delete', None, 'fr')
        self.assertEquals(set(self.portal.available_languages),
                          set(['en','de']))

    def test_manageCPSLanguages_delete_too_much(self):
        # can't remove all the langs
        before = self.portal.available_languages
        utils.manageCPSLanguage(self.portal, 'delete', None, before)
        self.assertEquals(set(self.portal.available_languages), set(before))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    suite.addTest(unittest.makeSuite(IntegrationTestUtils))
    return suite

