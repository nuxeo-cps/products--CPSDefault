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
from funkload.CPSTestCase import CPSTestCase
from funkload.utils import xmlrpc_get_credential, xmlrpc_list_credentials

class CpsRemoteController(CPSTestCase):
    """The funktional test case.

    This test use a configuration file CpsRemoteController.conf.
    """

    def setUp(self):
        """Setting up test."""
        self.logd("setUp.")
        server_url = self.conf_get('main', 'url')
        if not server_url.endswith('portal_remote_controller'):
            server_url += '/portal_remote_controller'
        self.server_url = server_url
        credential_host = self.conf_get('credential', 'host')
        credential_port = self.conf_getInt('credential', 'port')
        cred = xmlrpc_get_credential(credential_host,
                                     credential_port,
                                     'AdminZope')
        self.cred_admin = cred
        self.setBasicAuth(*cred)
        self.section_title = 'FunkLoad test' # Watchout title should generate
        self.section_id = 'funkload-test'    # this id
        self.workspace_title = 'FunkLoad test'
        self.workspace_id = 'funkload-test'


    def test_00_availability(self):
        # test to wait until the zope server is up and running
        server_url = self.server_url.replace('/portal_remote_controller', '')
        zope_url, site_id = self.cpsGuessZopeUrl()
        self.waitUntilAvailable(zope_url, 30, 2)

    def test_05_verify_RemoteController(self):
        server_url = self.server_url
        if not self.exists(server_url):
            server_url = self.server_url.replace('/portal_remote_controller',
                                                 '')
            self.logd('Creating a portal_remote_controller')
            self.zopeAddExternalMethod(server_url, self.cred_admin[0],
                                       self.cred_admin[1],
                                       'portal_remote_controller',
                                       'CPSRemoteController.install',
                                       'install')

    def test_10_getVersion(self):
        server_url = self.server_url
        product_name = 'CPSRemoteController'
        ret = self.xmlrpc_call(server_url, 'getProductVersion',
                               [product_name],
                               description="get %s version" % product_name)
        self.logd('ret %s' % ret)


    def test_20_createDocument(self):
        nb_docs = self.conf_getInt('test_20_createDocument', 'nb_docs')
        for i in range(nb_docs):
            language = self.cpsGetRandomLanguage()
            ret = self.xmlrpc_call(
                self.server_url, 'createDocument',
                ['Document',
                 {'Title': self._lipsum.getSubject(uniq=True,
                                                   prefix='test '+ language),
                  'Description': self._lipsum.getSubject(10),
                  'LanguageSelectorCreation': language,
                  'content_rformat': "text",
                  'content': self._lipsum.getMessage(),
                  },
                 "workspaces/%s" % self.workspace_id,
                 ],
                description="Create document")
            self.logd('ret %s' % ret)


    def tearDown(self):
        """Setting up test."""
        self.clearBasicAuth()
        self.logd("tearDown.")


if __name__ in ('main', '__main__'):
    # even if fl-run-test is much better
    unittest.main()
