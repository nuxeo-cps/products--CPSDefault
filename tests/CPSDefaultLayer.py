# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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

import os
import time
import transaction
from Testing import ZopeTestCase
from zope.app.testing.functional import ZCMLLayer
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

#from Products.CPSDefault.tests.CPSTestCase import PORTAL_ID
#from Products.CPSDefault.tests.CPSTestCase import CPSInstaller

PROFILE_ID = 'CPSDefault:default'
PORTAL_ID = 'portal'
MANAGER_ID = 'manager'
MANAGER_EMAIL = 'webmaster@localhost'
MANAGER_PASSWORD = 'passwd'


config_file = 'cpsdefaultlayer.zcml'
config_file = os.path.join(os.path.dirname(__file__), config_file)

CPSZCMLLayer = ZCMLLayer(config_file, __name__, 'CPSZCMLLayer')


class CPSDefaultLayerClass(object):
    """Layer to test CPS.

    The goal of a testrunner layer is to isolate initializations common
    to a lot of testcases. The setUp of the layer is run only once, then
    all tests for the testcases belonging to the layer are run.
    """

    # The setUp of bases is called autmatically first
    __bases__ = (CPSZCMLLayer,)

    def __init__(self, module, name):
        self.__module__ = module
        self.__name__ = name

    def setUp(self):
        self.setSynchronous()
        self.app = ZopeTestCase.app()
        self.install()

    def tearDown(self):
        self.unSetSynchronous()

    def setSynchronous(self):
        # During setup and tests we want synchronous indexing.
        from Products.CPSCore.IndexationManager import get_indexation_manager
        from Products.CPSCore.IndexationManager import IndexationManager
        IndexationManager.DEFAULT_SYNC = True # Monkey patch
        get_indexation_manager().setSynchronous(True) # Current transaction

    def unSetSynchronous(self):
        from Products.CPSCore.IndexationManager import IndexationManager
        IndexationManager.DEFAULT_SYNC = False # Monkey patch

    def install(self):
        self.addRootUser()
        self.login()
        self.addPortal()
        #self.fixupTranslationServices(portal_id)
        #self.setupCPSSkins(portal_id)
        self.logout()
        transaction.commit()

    def addRootUser(self):
        aclu = self.app.acl_users
        aclu._doAddUser('CPSTestCase', '', ['Manager'], [])

    def login(self):
        aclu = self.app.acl_users
        user = aclu.getUserById('CPSTestCase').__of__(aclu)
        newSecurityManager(None, user)

    def addPortal(self):
        from Products.CPSDefault.factory import addConfiguredCPSSite
        addConfiguredCPSSite(self.app,
                             profile_id=PROFILE_ID,
                             snapshot=False,
                             site_id=PORTAL_ID,
                             title='CPSDefault Portal',
                             languages=['en', 'fr', 'de'],
                             manager_id=MANAGER_ID,
                             manager_email=MANAGER_EMAIL,
                             password=MANAGER_PASSWORD,
                             password_confirm=MANAGER_PASSWORD,
                             )

    def logout(self):
        noSecurityManager()


CPSDefaultLayer = CPSDefaultLayerClass(__name__, 'CPSDefaultLayer')


class ExtensionProfileLayerClass(object):

    __bases__ = (CPSDefaultLayer,)

    extension_ids = ()

    def __init__(self, module, name):
        self.__module__ = module
        self.__name__ = name

    def setUp(self):
        app = ZopeTestCase.app()
        tool = getattr(app, PORTAL_ID).portal_setup
        for extension_id in self.extension_ids:
            tool.setImportContext('profile-%s' % extension_id)
            tool.runAllImportSteps()
        tool.setImportContext('profile-%s' % PROFILE_ID)
        transaction.commit()

    def tearDown(self):
        pass
