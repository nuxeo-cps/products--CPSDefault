import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSDefaultTestCase

from Products.CMFCore.tests.base.utils import has_path


class TestI18n(CPSDefaultTestCase.CPSDefaultTestCase):
    login_id = 'manager'
    def afterSetUp(self):
        if self.login_id:
            self.login(self.login_id)
            self.portal.portal_membership.createMemberArea()

        # Some ZPTs need a session.
        # XXX: this might be moved to a more generic place someday.
        self.portal.REQUEST.SESSION = {}
        self.default_lang = 'en'

    def beforeTearDown(self):
        self.logout()

    def testI18nZpt(self):
        for folder in (self.portal.workspaces, self.portal.sections):
            self.assert_(folder.content_translate_form())

    def testNonI18nFolder(self):
        ws = self.portal.workspaces
        catalog = self.portal.portal_catalog

        #print "xxxx creation"
        proxy_id = 'a_non_i18n_workspace'
        ws.invokeFactory('Workspace', proxy_id)
        proxy = getattr(ws, proxy_id)
        doc = proxy.getContent()

        self.assert_(len(proxy.Languages()) == 1)
        self.assert_(self.default_lang in proxy.Languages())
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
        #print "xxxx creation"
        ws.invokeFactory('Workspace', proxy_id)
        proxy = getattr(ws, proxy_id)
        doc_def = proxy.getContent()

        #print "xxxx creation fr"
        self.portal.content_translate(lang='fr', proxy=proxy)
        # XXX this should have been done by content_transalte
        proxy.reindexObject()

        doc_fr = proxy.getContent(lang='fr')
        self.assert_(doc_fr.Language() == 'fr')

        languages = proxy.Languages()
        self.assert_('en' in languages)
        self.assert_('fr' in languages)
        self.assert_(not has_path(catalog, "/portal/workspaces/"+proxy_id))
        self.assert_(
            has_path(catalog,
                     "/portal/workspaces/"+proxy_id+"/viewLanguage/fr"))
        self.assert_(
            has_path(catalog,
                     "/portal/workspaces/"+proxy_id+"/viewLanguage/en"))

        ## XXX this does not work for the moment
        ## catalog keep viewLanguage/xx path

        ##print "xxxx deletion of fr rev"
        #proxy.delLanguageFromProxy(lang='fr')
        #proxy.reindexObject()

        #languages = proxy.Languages()
        #self.assert_('en' in languages)
        #self.assert_(len(languages) == 1)
        #self.assert_(has_path(catalog, "/portal/workspaces/a_workspace"))
        # YYYYYYYYYYYYYYYYYYYYYYYYYYYYYY failed
        #self.assert_(
        #    not has_path(catalog,
        #                 "/portal/workspaces/a_workspace/viewLanguage/fr"))
        #self.assert_(
        #    not has_path(catalog,
        #                 "/portal/workspaces/a_workspace/viewLanguage/en"))

        #print "xxxx deletion of proxy"
        self.portal.portal_eventservice.notifyEvent('workflow_delete',
                                                    proxy,
                                                    {})
        ws.manage_delObjects(proxy_id)

        self.assert_(proxy_id not in ws.objectIds())
        self.assert_(not has_path(catalog, "/portal/workspaces/"+proxy_id))
        self.assert_(not has_path(catalog, "/portal/workspaces/"+proxy_id+"/viewLanguage/fr"))
        self.assert_(not has_path(catalog, "/portal/workspaces/"+proxy_id+"/viewLanguage/en"))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestI18n))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)
