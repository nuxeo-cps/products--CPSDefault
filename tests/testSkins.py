# -*- coding: iso-8859-15 -*-

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from Products.CMFCore.tests.base.utils import has_path


# Testing some skins methods and templates anonymously.

class TestSkins(CPSDefaultTestCase.CPSDefaultTestCase):

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
        SKIN_NAMES = ['nuxeo_css1.css', 'nuxeo_css2.css', 'nuxeo_print_css.css',
            'nuxeo_print_css.css']

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
        id = "Voil� l'�t�"
        self.assertEquals(self.portal.computeId(id), "voila_l_ete")

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
