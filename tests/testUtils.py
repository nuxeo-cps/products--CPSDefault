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

class TestUtils(ZopeTestCase):

    def afterSetUp(self):
        self.folder.default_charset = 'unicode'

    def test_getNonArchivedVersionContextUrl(self):
        url0 = 'http://toto.com/titi/archivedRevision/123'
        url1 = 'http://toto.com/titi'
        self.assertEquals(utils.getNonArchivedVersionContextUrl(url0), url1)

    def test_computeContributors_anonymous(self):
        folder = self.folder
        self.logout()
        self.assertEquals(utils.computeContributors(folder, []),
                          [u'Anonymous User'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite

