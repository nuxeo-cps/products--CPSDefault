# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
# M.-A. Darche <ma.darche@cynode.org>
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
"""CPS basic navigation funkload test
"""
import unittest
import random
from funkload.CPSTestCase import CPSTestCase
from funkload.utils import xmlrpc_get_credential, xmlrpc_list_credentials
from types import DictType

class Cps(CPSTestCase):
    """The funktional test case.

    This test use a configuration file Cps.conf.
    """

    def setUp(self):
        """Setting up test."""
        self.logd("setUp.")
        self.server_url = self.conf_get('main', 'url')
        credential_host = self.conf_get('credential', 'host')
        credential_port = self.conf_getInt('credential', 'port')

        self.cred_admin = xmlrpc_get_credential(credential_host,
                                                credential_port,
                                                'AdminZope')
        self.cred_manager =  xmlrpc_get_credential(credential_host,
                                                   credential_port,
                                                   'AdminCps')
        self.cred_member = xmlrpc_get_credential(credential_host,
                                                 credential_port,
                                                 'FL_Member')
        self.cred_reviewer = xmlrpc_get_credential(credential_host,
                                                   credential_port,
                                                   'FL_Reviewer')
        self.credential_host = credential_host
        self.credential_port = credential_port
        self.section_title = 'FunkLoad test' # Watchout title should generate
        self.section_id = 'funkload-test'    # this id
        self.workspace_title = 'FunkLoad test'
        self.workspace_id = 'funkload-test'
        self.sub_workspace_num = 10
        self.sub_section_num = 10
        if self.cps_test_case_version >= (3, 4, 0):
            self.members_home = 'members'
        else:
            self.members_home = 'workspaces/members'

    def test_00_availability(self):
        # test to wait until the zope server is up and running
        server_url = self.server_url
        zope_url, site_id = self.cpsGuessZopeUrl()
        self.waitUntilAvailable(zope_url, 30, 2)

    def test_01_verif_cps(self):
        server_url = self.server_url
        if not self.exists(server_url):
            langs = self.conf_getList('main', 'languages')
            manager_mail = self.conf_get('test_01_verif_cps', 'manager_mail')
            self.cpsCreateSite(self.cred_admin[0], self.cred_admin[1],
                               self.cred_manager[0], self.cred_manager[1],
                               manager_mail, langs=langs,
                               title="Cps Funkload Test Site")

    def test_05_verif_groups(self):
        server_url = self.server_url
        self.cpsLogin(self.cred_manager[0], self.cred_manager[1], "manager")
        for group in ('FL_Member', 'FL_Reviewer', 'FL_Manager'):
            self.cpsVerifyGroup(group)
        self.cpsLogout()

    def test_06_verif_users(self):
        server_url = self.server_url
        self.cpsLogin(self.cred_manager[0], self.cred_manager[1], "manager")
        for group in ('FL_Member', 'FL_Reviewer', 'FL_Manager'):
            for user_id, user_pwd in xmlrpc_list_credentials(
                self.credential_host, self.credential_port, group):
                self.cpsVerifyUser(user_id=user_id,
                                   user_pwd=user_pwd,
                                   groups=[group])
        self.cpsLogout()

    def test_10_create_doc(self):
        nb_docs = self.conf_getInt('test_10_create_doc', 'nb_docs')
        server_url = self.server_url
        login = self.cred_member[0]
        self.cpsLogin(login, self.cred_member[1], "member")
        for i in range(nb_docs):
            self.cpsCreateNewsItem("%s/%s/%s" %
                                   (server_url, self.members_home, login),
                                   photo_path="photo.jpg")
        self.cpsLogout()

    def test_20_verif_folders(self):
        server_url = self.server_url
        self.cpsLogin(self.cred_manager[0], self.cred_manager[1], "manager")

        # check if we have a BtreeWokspace available
        if self.exists("%s/portal_types/BtreeWorkspace/manage_propertiesForm" % server_url):
            self.logd('Use Btree Workspace')
            workspace_type = 'BtreeWorkspace'
        else:
            self.logd('No BtreeWorkspace available use default Workspace.')
            workspace_type = 'Workspace'

        section_url = '%s/sections/%s' % (server_url, self.section_id)
        if not self.exists(section_url):
            rurl = self.cpsCreateSection(
                '%s/sections' % server_url, self.section_title,
                'This is a FunkLoad test section, see '
                'http://pypi.python.org/pypi/funkload'
                'for more information.')
            url = '%s/%s' % (server_url, rurl)
            self.cpsSetLocalRole(url, 'group:FL_Manager', 'SectionManager')
            self.cpsSetLocalRole(url, 'group:FL_Reviewer', 'SectionReviewer')
            self.cpsSetLocalRole(url, 'group:FL_Member', 'SectionReader')
        workspace_url = '%s/workspaces/%s' % (server_url, self.workspace_id)
        if not self.exists(workspace_url):
            rurl = self.cpsCreateWorkspace(
                '%s/workspaces' % server_url, self.workspace_title,
                'This is a FunkLoad test workspace, see '
                'http://pypi.python.org/pypi/funkload'
                'for more information.')
            url = '%s/%s' % (server_url, rurl)
            self.cpsSetLocalRole(url, 'group:FL_Manager', 'WorkspaceManager')
            self.cpsSetLocalRole(url, 'group:FL_Member', 'WorkspaceMember')
        for i in range(self.sub_workspace_num):
            sub_workspace_title = 'Sub workspace %.2d' % i
            sub_workspace_url = workspace_url + '/sub-workspace-%.2d' % i
            if not self.exists(sub_workspace_url):
                rurl = self.cpsCreateFolder(workspace_type, workspace_url,
                                            sub_workspace_title,
                                            'FunkLoad sub workspace %d' % i,
                                            self.cpsGetRandomLanguage())
        for i in range(self.sub_section_num):
            sub_section_title = 'Sub section %.2d' % i
            sub_section_url = section_url + '/sub-section-%.2d' % i
            if not self.exists(sub_section_url):
                rurl = self.cpsCreateSection(section_url,
                                             sub_section_title,
                                             'FunkLoad sub section %d' % i)
        self.cpsLogout()


    def test_21_create_doc(self):
        nb_docs = self.conf_getInt('test_10_create_doc', 'nb_docs')
        server_url = self.server_url
        login = self.cred_member[0]
        self.cpsLogin(login, self.cred_member[1], "member")
        for i in range(nb_docs):
            ws_num = random.random() * self.sub_workspace_num
            workspace_id = 'sub-workspace-%.2d' % ws_num
            self.cpsCreateNewsItem("%s/workspaces/%s/%s" % (server_url,
                                                            self.workspace_id,
                                                            workspace_id),
                                   photo_path="photo.jpg")
        self.cpsLogout()


    def test_22_publish(self):
        server_url = self.server_url
        base_url = '%s/workspaces/%s' % (server_url, self.workspace_id)
        # begin of ftest ---------------------------------------------

        # login in as member -----------------------------------------
        self.cpsLogin(self.cred_member[0], self.cred_member[1],
                      "member")
        # access test ws
        self.get("%s/folder_contents" % base_url,
                 description="Folder contents")

        # create a document
        doc_rurl, doc_id = self.cpsCreateNewsItem(base_url,
                                                  photo_path="photo.jpg")

        # pubish a doc
        doc_url = server_url + '/' + doc_rurl
        self.get("%s/content_submit_form" % doc_url,
                 description="View submit form")
        params = [["submit", "sections/%s" % self.section_id],
                  ["comments", "ftest submit"],
                  ["workflow_action", "copy_submit"]]
        self.post("%s/content_status_modify" % doc_url, params,
                  description="Submit the document")
        self.assert_(self.getLastUrl().find('psm_status_changed') != -1,
                     'Failed to publish %s into sections/%s' % (
            doc_rurl, self.section_id))

        # we sould see only one doc_id
        #self.assertEquals(len(self.cpsSearchDocId(doc_id)), 1,
        #"should see only one doc_id [%s]." % doc_id)
        self.cpsLogout()


        # login as reviewer ---------------------------------------
        self.cpsLogin(self.cred_reviewer[0],
                      self.cred_reviewer[1],
                      "reviewer")

        # accept the doc
        base_url2 = "%s/sections/%s" % (server_url, self.section_id)
        doc_publish_url = "%s/%s" % (base_url2, doc_id)
        self.get("%s/content_accept_form" % doc_publish_url,
                 description="View the accept form")
        params = [["comments", "Nice work %s" % self.cred_member[0]],
                  ["workflow_action", "accept"]]
        self.post("%s/content_status_modify" % doc_publish_url, params,
                  description="Accept the document")
        self.assert_(self.getLastUrl().find('psm_status_changed') != -1,
                     'Failed to accept %s' % doc_publish_url)

        # check that we have 2 doc_ids
        #self.assertEquals(len(self.cpsSearchDocId(doc_id)), 2,
        #                  "should see only one doc_id [%s]." % doc_id)
        self.cpsLogout()
        # end of ftest -----------------------------------------------
        return self.steps

    def test_30_reader_anonymous(self):
        server_url = self.server_url
        self.get('%s' % server_url,
                 description='Home page anonymous')

        #self.assert_(self.listHref('login_form'), 'No login link found')

        self.get('%s/login_form' % server_url,
                 description="Login page")

        self.get("%s/accessibility" % server_url,
                 description="View accessibility information")

        self.get("%s/advanced_search_form" % server_url,
                 description="View advanced search form")

        # home page in different languages
        self.get('%s/' % server_url, description="Home page anonymous")
        languages = self.conf_getList('main', 'languages')
        languages.reverse()             # to end with the first default one
        for lang in languages:
            # this will reload home page using a different locale
            self.cpsChangeUiLanguage(lang)

        # XXX TODO check that private page are unaccessible


    def test_31_reader_member(self):
        server_url = self.server_url
        self.cpsLogin(self.cred_member[0], self.cred_member[1],
                      "member")

        self.get("%s/" % server_url, description="Home page logged")

        # home page in different languages
        languages = self.conf_getList('main', 'languages')
        languages.reverse()             # to end with the first default one
        for lang in languages:
            self.cpsChangeUiLanguage(lang)
            self.get(server_url, description="Logged home page in %s" % lang)

        # perso ws
        self.get("%s/%s/%s" % (server_url, self.members_home, self._cps_login),
                 description="View personal workspace")


        # test ws
        test_ws_url = '%s/workspaces/%s' % (server_url, self.workspace_id)
        self.get(test_ws_url, description="View FL test workspace")

        # view a random document
        docs = self.cpsListDocumentHref('workspaces/%s/test-' %
                                        self.workspace_id)
        self.assert_(docs, "no doc found in ws %s" % self.workspace_id)

        a_doc = docs[int(len(docs) * random.random())]
        self.get("%s%s" % (server_url, a_doc),
                 description="View a document")

        # metadata
        self.get("%s%s/cpsdocument_metadata" % (server_url, a_doc),
                 description="View a document metadata")

        # export rss / atom
##         self.get("%s/exportRssContentBox?box_url=.cps_boxes_root/nav_content"
##                  % test_ws_url, description="View workspace RSS content")

##         self.get("%s/exportAtomContentBox?box_url=.cps_boxes_root/nav_content"
##                  % test_ws_url, description="View workspace Atom flux")

        # section
        self.get("%s/sections/%s" % (server_url, self.section_id),
                 description="View FL test section")

        # extract a doc link
        docs = self.cpsListDocumentHref('/sections/%s/test-' % self.section_id)
        self.assert_(docs, "no doc found in section %s" % self.section_id)
        a_doc = docs[int(len(docs) * random.random())]

        self.get("%s%s" % (server_url, a_doc),
                 description="View a published document")

        self.get("%s%s/cpsdocument_metadata" % (server_url, a_doc),
                 description="View a published document metadata")

        self.get("%s%s/content_status_history" % (server_url, a_doc),
                 description="View a published document history")

        # access common cps pages
        self.get("%s/manage_my_subscriptions_form" % server_url,
                 description="View my subscription page.")

        self.get("%s/cpsdirectory_view" % server_url,
                 description="View directories")

        params = [["dirname", "members"]]
        self.get("%s/cpsdirectory_entry_search_form" % server_url, params,
                 description="View member directory search form")

        params = [["dirname", "members"],
                  ["id", self._cps_login]]
        self.get("%s/cpsdirectory_entry_view" % server_url, params,
                 description="View user directory entry")

        self.cpsLogout()



    def test_tuning(self):
        server_url = self.server_url
        self.cpsLogin(self.cred_member[0], self.cred_member[1],
                      "member")

        self.get("%s/" % server_url, description="Home page logged")

        # perso ws
        self.get("%s/%s/%s" % (server_url, self.members_home, self._cps_login),
                 description="View personal workspace")

        # test ws
        test_ws_url = '%s/workspaces/%s' % (server_url, self.workspace_id)
        self.get(test_ws_url, description="View FL test workspace")


        # get a random document
        docs = self.cpsListDocumentHref('workspaces/%s/test-' %
                                        self.workspace_id)
        self.assert_(docs, "no doc found in ws %s" % self.workspace_id)

        a_doc = docs[int(len(docs) * random.random())]

        self.get(test_ws_url+ '/folder_factories',
                 description="View Folder factories")

        self.get("%s%s?emptybody=1" % (server_url, a_doc),
                 description="View a document")

        self.get("%s%s/cpsdocument_metadata" % (server_url, a_doc),
                 description="View a document metadata")

        self.get("%s%s/cpsdocument_edit_form" % (server_url, a_doc),
                 description="View document edition")


        # section
        self.get("%s/sections/%s" % (server_url, self.section_id),
                 description="View FL test section")

        # extract a doc link
        docs = self.cpsListDocumentHref('/sections/%s/test-' % self.section_id)
        self.assert_(docs, "no doc found in section %s" % self.section_id)
        a_doc = docs[int(len(docs) * random.random())]

        self.get("%s%s" % (server_url, a_doc),
                 description="View a published document")

        self.get("%s%s/cpsdocument_metadata" % (server_url, a_doc),
                 description="View a published document metadata")

        self.get("%s%s/content_status_history" % (server_url, a_doc),
                 description="View a published document history")

        self.cpsLogout()

    def test_tuning2(self):
        server_url = self.server_url
        login = self.cred_member[0]
        self.cpsLogin(login, self.cred_member[1], "member")


        workspace_url = '%s/workspaces/%s' % (server_url, self.workspace_id)
        self.get(workspace_url + '/cpsdocument_create_form?widget__Title=foo&type_name=Document', description="View create form")
        self.cpsCreateDocument(workspace_url)
        self.cpsLogout()


    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.")



class CpsLightSkin(Cps):
    """Same as Cps but post and get will add an extra pp parameters.

    This ask cps to render the printable light skin.
    This test use a configuration file CpsLightSkin.conf.
    """
    def get(self, url, params=None, description=None, ok_codes=None):
        """Patch to add params pp=1 to use a print skins."""
        if params is None:
            params = {'pp': '1'}
        else:
            if type(params) is DictType:
                params['pp'] = '1'
            else:
                params.append(['pp', '1'])
        return CPSTestCase.get(self, url, params, description, ok_codes)

    def post(self, url, params=None, description=None, ok_codes=None):
        """Patch to add params pp=1 to use a print skins."""
        if params is None:
            params = {'pp': '1'}
        else:
            if type(params) is DictType:
                params['pp'] = '1'
            else:
                params.append(['pp', '1'])
        return CPSTestCase.post(self, url, params, description, ok_codes)



if __name__ in ('main', '__main__'):
    # even if fl-run-test is much better
    unittest.main()
