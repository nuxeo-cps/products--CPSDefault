import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from Products.CMFCore.tests.base.utils import has_path
from Products.CPSCore.utils import KEYWORD_SWITCH_LANGUAGE
from Products.CPSCore.utils import KEYWORD_VIEW_LANGUAGE
from Products.CPSCore.utils import resetRequestLanguageSelection

class TestI18n(CPSDefaultTestCase.CPSDefaultTestCase):
    login_id = 'manager'
    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()
        self.default_lang = 'en'

    def beforeTearDown(self):
        self.logout()

    def testI18nZpt(self):
        for folder in (self.portal.workspaces, self.portal.sections):
            self.assert_(folder.content_translate_form())

    def testNonI18nFolder(self):
        # this a normal ws with only one locale
        ws = self.portal.workspaces
        catalog = self.portal.portal_catalog

        #print "xxxx creation"
        proxy_id = 'a_non_i18n_workspace'
        ws.invokeFactory('Workspace', proxy_id)
        proxy = getattr(ws, proxy_id)
        doc = proxy.getContent()

        self.assert_(len(proxy.getProxyLanguages()) == 1)
        self.assert_(self.default_lang in proxy.getProxyLanguages())
        self.assert_(doc.Language() == self.default_lang)
        self.assert_(has_path(catalog, "/portal/workspaces/"+proxy_id))

        #print "xxxx deletion"
        self.portal.portal_eventservice.notifyEvent('workflow_delete',
                                                    proxy,
                                                    {})
        ws.manage_delObjects(proxy_id)

        self.assert_(proxy_id not in ws.objectIds())
        self.assert_(not has_path(catalog, "/portal/workspaces/"+proxy_id))


    def testI18nFolder(self):
        catalog = self.portal.portal_catalog
        ws = self.portal.workspaces
        proxy_id = 'a_workspace'
        default_lang = self.default_lang

        #print "creation --------------------"
        ws.invokeFactory('Workspace', proxy_id)
        proxy = getattr(ws, proxy_id)
        doc_def = proxy.getContent()

        #print "creation fr --------------------"
        new_lang = 'fr'
        self.portal.content_translate(lang=new_lang, proxy=proxy)

        doc_new = proxy.getContent(lang=new_lang)
        self.assert_(doc_new.Language() == new_lang)

        languages = proxy.getProxyLanguages()
        self.assert_(default_lang in languages)
        self.assert_(new_lang in languages)
        self.assert_(not has_path(catalog, "/portal/workspaces/"+proxy_id))
        self.assert_(has_path(catalog, "/portal/workspaces/%s/%s/%s" % (
            proxy_id, KEYWORD_VIEW_LANGUAGE, new_lang)))
        self.assert_(has_path(catalog, "/portal/workspaces/%s/%s/%s" % (
            proxy_id, KEYWORD_VIEW_LANGUAGE, default_lang)))

        #print "checking switchLanguage  --------------------"
        resetRequestLanguageSelection(self.portal.REQUEST)
        for lang in languages:
            proxy_tmp = self.portal.unrestrictedTraverse(
                "/portal/workspaces/%s/%s/%s" % (proxy_id,
                                                 KEYWORD_SWITCH_LANGUAGE,
                                                 lang))
            doc = proxy.getContent()
            self.assertEquals(doc.Language(), lang)

        #print "checking viewLanguage  --------------------"
        resetRequestLanguageSelection(self.portal.REQUEST)
        for lang in languages:
            proxy_tmp = self.portal.unrestrictedTraverse(
                "/portal/workspaces/%s/%s/%s" % (proxy_id,
                                                 KEYWORD_VIEW_LANGUAGE,lang))
            doc = proxy.getContent()
            self.assertEquals(doc.Language(), lang)

        #print "checking priority of viewLanguage --------------------"
        proxy_v = self.portal.unrestrictedTraverse(
            "/portal/workspaces/%s/%s/%s" % (proxy_id, KEYWORD_VIEW_LANGUAGE,
                                             new_lang))
        proxy_s = self.portal.unrestrictedTraverse(
            "/portal/workspaces/%s/%s/%s" % (proxy_id,
                                             KEYWORD_SWITCH_LANGUAGE,
                                             default_lang))
        doc = proxy.getContent()
        self.assertEquals(doc.Language(), new_lang)

        #print "deletion of the fr locale --------------------"
        self.portal.content_delete_translation(proxy=proxy, lang='fr')
        languages = proxy.getProxyLanguages()
        self.assert_('en' in languages)
        self.assert_(len(languages) == 1)
        self.assert_(has_path(catalog, "/portal/workspaces/a_workspace"))
        self.assert_(
            not has_path(catalog,
                         "/portal/workspaces/a_workspace/viewLanguage/fr"))
        self.assert_(
            not has_path(catalog,
                         "/portal/workspaces/a_workspace/viewLanguage/en"))

        #print "deletion of the proxy --------------------"
        self.portal.portal_eventservice.notifyEvent('workflow_delete',
                                                    proxy,
                                                    {})
        ws.manage_delObjects(proxy_id)

        self.assert_(proxy_id not in ws.objectIds())
        self.assert_(not has_path(catalog, "/portal/workspaces/"+proxy_id))
        self.assert_(not has_path(catalog, "/portal/workspaces/%s/%s/%s" % (
                proxy_id, KEYWORD_VIEW_LANGUAGE, 'fr')))
        self.assert_(not has_path(catalog, "/portal/workspaces/%s/%s/%s" % (
                proxy_id, KEYWORD_VIEW_LANGUAGE, 'en')))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestI18n))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
