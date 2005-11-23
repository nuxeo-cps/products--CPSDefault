# -*- coding: iso-8859-15 -*-
# Copyright (c) 2005 Nuxeo SAS <http://nuxeo.com>
# Author : Julien Anguenot <ja@nuxeo.com>
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
""" Test various versionning features
"""

import unittest
import CPSDefaultTestCase

class VersionningTestCaseBase(CPSDefaultTestCase.CPSDefaultTestCase):

    def afterSetUp(self):
        self._ws = self.portal.workspaces
        self._sc = self.portal.sections
        self._wftool = self.portal.portal_workflow
        self._pxtool = self.portal.portal_proxies

    def beforeTearDown(self):
        self.logout()

    def _createObject(self, where, type_name):
        id_ = where.computeId()
        self._wftool.invokeFactoryFor(where, type_name, id_)
        return id_

    def _publishObject(self, proxy, where):
        self._wftool.doActionFor(proxy, 'copy_submit',
                                 dest_container='sections',
                                 initial_transition='publish')

    def _createNewRevisionFor(self, proxy):
        """Create a new revision for a given proxy
        """
        self._pxtool.freezeProxy(proxy)
        proxy.getEditableContent()

    def _getLanguageRevsFor(self, proxy):
        docid = proxy.getDocid()
        proxy_info = self._pxtool.getProxyInfosFromDocid(docid)
        for info in proxy_info:
            if info['object'] == proxy:
                return info['language_revs']
        return {}

class TranslationTestCase(VersionningTestCaseBase):

    # https://svn.nuxeo.org/trac/pub/ticket/603

    login_id = 'manager'

    def afterSetUp(self):
        self.login(self.login_id)
        VersionningTestCaseBase.afterSetUp(self)

    def test_translate(self):

        #
        # Create a revision (v1, en)
        #

        id_ = self._createObject(self._ws, 'File')
        proxy = getattr(self._ws, id_)
        self.assertEqual(self._getLanguageRevsFor(proxy), {'en': 1})

        #
        # Publish this to sections
        #

        self._publishObject(proxy, self._sc)

        # Check the wokspace one
        proxy = getattr(self._ws, id_)
        self.assertEqual(self._getLanguageRevsFor(proxy), {'en': 1})

        # Check the section one
        proxy_published = getattr(self._sc, id_)
        self.assertEqual(self._getLanguageRevsFor(proxy_published), {'en': 1})

        #
        # Translate the workspace v1 to french
        #

        self._wftool.doActionFor(proxy, 'translate', comment='',
                                 lang='fr', from_lang='en')

        proxy = getattr(self._ws, id_)
        self.assertEqual(self._getLanguageRevsFor(proxy), {'fr': 2, 'en': 1})


        self._publishObject(proxy, self._sc)

        # Check the wokspace one
        proxy = getattr(self._ws, id_)
        self.assertEqual(self._getLanguageRevsFor(proxy), {'fr': 2, 'en': 1})

        # Check the section one
        proxy_published = getattr(self._sc, id_)
        self.assertEqual(
            self._getLanguageRevsFor(proxy_published), {'fr': 2, 'en': 1})

        #
        # Translate again
        #

        proxy = getattr(self._ws, id_)
        self._wftool.doActionFor(proxy, 'translate', comment='',
                                 lang='it', from_lang='en')

        proxy = getattr(self._ws, id_)
        self.assertEqual(
            self._getLanguageRevsFor(proxy), {'it': 3, 'fr': 2, 'en': 1})


        self._publishObject(proxy, self._sc)

        # Check the wokspace one
        proxy = getattr(self._ws, id_)
        self.assertEqual(
            self._getLanguageRevsFor(proxy), {'it': 3, 'fr': 2, 'en': 1})

        # Check the section one
        proxy_published = getattr(self._sc, id_)
        self.assertEqual(
            self._getLanguageRevsFor(proxy_published),
            {'it': 3, 'fr': 2, 'en': 1})

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TranslationTestCase))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
