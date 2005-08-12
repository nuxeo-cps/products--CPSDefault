# -*- coding: iso-8859-15 -*-

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.tests.base.utils import has_path
#ZopeTestCase.installProduct('VerboseSecurity', quiet=1)


# Testing some skins methods and templates anonymously.

class TestSkins(CPSDefaultTestCase.CPSDefaultTestCase):

    login_id = 'manager'

    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
        self.wftool  = getToolByName(self.portal, 'portal_workflow')

    def beforeTearDown(self):
        self.logout()

    def testTemplates(self):
        self.assert_(self.portal.index_html())
        self.assert_(self.portal.login_form())
        self.assert_(self.portal.join_form())
        self.assert_(self.portal.search_form())
        self.assert_(self.portal.advanced_search_form())

    def testJavaScripts(self):
        request = self.portal.REQUEST
        self.assert_(getattr(self.portal, 'functions.js')(REQUEST=request))
        self.assert_(getattr(self.portal, 'rss.js')(REQUEST=request))

    def testCSSProperties(self):
        self.assert_(self.portal.stylesheet_properties)
        self.assert_(self.portal.stylesheet_properties.mainBackground)

    def testCSS(self):
        SKIN_NAMES = ['default.css', 'default_print.css']

        # These are DTML -> need to call them.
        request = self.portal.REQUEST
        for css_name in SKIN_NAMES:
            css = getattr(self.portal, css_name)
            # HACK: without this hack, we get a strange error
            self.assert_(css(
                REQUEST=self.portal.REQUEST,
                stylesheet_properties=self.portal.stylesheet_properties))

        # No need to call, it's a file.
        self.assert_(getattr(self.portal, 'msie.css'))

    def testComputeId(self):
        # Testing that computeId generates different IDs if the ID is already
        # used in the same container.
        s = 'Special ID that we want to be unique'
        workspaces = self.portal.workspaces
        id1 = workspaces.computeId(s)
        self.wftool.invokeFactoryFor(workspaces, 'File', id1)
        id2 = workspaces.computeId(s)
        self.assertNotEquals(id1, id2)

        # URLs are computed differently and intelligently depending on the
        # specified locale, because meaningless words are removed.
        id = "Voilà l'été"
        self.assertEquals(self.portal.computeId(id, lang='fr'), "voila-ete")
        self.assertNotEquals(self.portal.computeId(id, lang='en'), "voila-ete")
        id = "This is a message from the president"
        self.assertEquals(self.portal.computeId(id, lang='en'),
                          "message-from-president")
        self.assertNotEquals(self.portal.computeId(id, lang='fr'),
                             "message-from-president")


    def testTruncURL(self):
        url = 'http://youpilala.com/il/fait/beau/et/chaud/ajourd/hui'
        self.assertEquals(self.portal.truncURL(url, 10), 'you...hui')

    def testGetBaseUrl(self):
        self.assertEquals(self.portal.getBaseUrl(), '/portal/')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSkins))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

