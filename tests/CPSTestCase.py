# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Stefane Fermigier <sf@nuxeo.com>
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

ZopeTestCase.installProduct('ZCTextIndex', quiet=1)
ZopeTestCase.installProduct('BTreeFolder2', quiet=1)
ZopeTestCase.installProduct('StandardCacheManagers', quiet=1)
ZopeTestCase.installProduct('Five', quiet=1)
ZopeTestCase.installProduct('SiteAccess', quiet=1)
ZopeTestCase.installProduct('MailHost', quiet=1)
# CMF
ZopeTestCase.installProduct('CMFCalendar', quiet=1)
ZopeTestCase.installProduct('CMFCore', quiet=1)
ZopeTestCase.installProduct('CMFDefault', quiet=1)
ZopeTestCase.installProduct('CMFTopic', quiet=1)
ZopeTestCase.installProduct('CMFSetup', quiet=1)
ZopeTestCase.installProduct('DCWorkflow', quiet=1)
# CPS
ZopeTestCase.installProduct('CPSDefault', quiet=1)
ZopeTestCase.installProduct('CPSCore', quiet=1)
ZopeTestCase.installProduct('CPSWorkflow', quiet=1)
ZopeTestCase.installProduct('CPSSchemas', quiet=1)
ZopeTestCase.installProduct('CPSDirectory', quiet=1)
ZopeTestCase.installProduct('CPSDocument', quiet=1)
ZopeTestCase.installProduct('CPSUserFolder', quiet=1)
ZopeTestCase.installProduct('Localizer', quiet=1)
ZopeTestCase.installProduct('TranslationService', quiet=1)
ZopeTestCase.installProduct('CPSSkins', quiet=1)
ZopeTestCase.installProduct('CPSPortlets', quiet=1)

# XXX AT: these products should be optional (dependencies remain to be checked)
ZopeTestCase.installProduct('CPSNavigation', quiet=1)
ZopeTestCase.installProduct('FCKeditor', quiet=1)
ZopeTestCase.installProduct('Epoz', quiet=1)
ZopeTestCase.installProduct('CPSSubscriptions', quiet=1)
ZopeTestCase.installProduct('CPSNewsLetters', quiet=1)
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('CPSWiki', quiet=1)
ZopeTestCase.installProduct('CPSBoxes', quiet=1)
ZopeTestCase.installProduct('CPSRSS', quiet=1)
ZopeTestCase.installProduct('CPSForum', quiet=1)
ZopeTestCase.installProduct('CPSOOo', quiet=1)
ZopeTestCase.installProduct('ExternalEditor', quiet=1)

import PatchLocalizer

# Better tracebacks
import traceback
from zExceptions.ExceptionFormatter import format_exception
traceback.format_exception = format_exception


PROFILE_ID = 'CPSDefault:default'
PORTAL_ID = 'portal'
MANAGER_ID = 'manager'
MANAGER_EMAIL = 'webmaster@localhost'
MANAGER_PASSWORD = 'passwd'

##################################################
# Layers

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

        # XXX: setupCPSSkins is not needed here, right ?
        #self.setupCPSSkins(portal_id)
        assert self.portal.portal_themes
        self.logout()
        transaction.commit()

    def addRootUser(self):
        aclu = self.app.acl_users
        aclu._doAddUser('CPSTestCase', '', ['Manager'], [])

    def login(self):
        aclu = self.app.acl_users
        user = aclu.getUserById('CPSTestCase').__of__(aclu)
        newSecurityManager(None, user)

    def logout(self):
        noSecurityManager()

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
                             manager_firstname="CPS",
                             manager_lastname="Manager",
                             )
        self.portal = getattr(self.app, PORTAL_ID)


CPSDefaultLayer = CPSDefaultLayerClass(__name__, 'CPSDefaultLayer')


class ExtensionProfileLayerClass(object):

    __bases__ = (CPSDefaultLayer,)

    extension_ids = ()

    def __init__(self, module, name):
        self.__module__ = module
        self.__name__ = name

    def setUp(self):
        self.app = ZopeTestCase.app()
        self.login()
        self.portal = getattr(self.app, PORTAL_ID)
        tool = self.portal.portal_setup
        for extension_id in self.extension_ids:
            tool.setImportContext('profile-%s' % extension_id)
            tool.runAllImportSteps()
        tool.setImportContext('profile-%s' % PROFILE_ID)
        transaction.commit()
        self.logout()

    def login(self):
        aclu = self.app.acl_users
        user = aclu.getUserById('CPSTestCase').__of__(aclu)
        newSecurityManager(None, user)

    def logout(self):
        noSecurityManager()

    def tearDown(self):
        pass

##################################################
# TestCase


class CPSTestCase(ZopeTestCase.PortalTestCase):

    layer = CPSDefaultLayer

    # configuration is already done in the layer
    _configure_portal = 0

    def _setup(self):
        ZopeTestCase.PortalTestCase._setup(self)

        # Some skins need sessions (not sure if it's a good thing).
        # Localizer too.
        # Both lines below are needed.
        SESSION = {}
        self.app.REQUEST['SESSION'] = SESSION
        self.app.REQUEST.SESSION = SESSION

    def printLogErrors(self, min_severity=0):
        """Print out the log output on the console.
        """
        import zLOG
        if hasattr(zLOG, 'old_log_write'):
            return
        def log_write(subsystem, severity, summary, detail, error,
                      PROBLEM=zLOG.PROBLEM, min_severity=min_severity):
            if severity >= min_severity:
                print "%s(%s): %s %s" % (subsystem, severity, summary, detail)
        zLOG.old_log_write = zLOG.log_write
        zLOG.log_write = log_write

    #
    # TODO: duplication -> refactor
    #
    def assertWellFormedXML(self, xml, page_id=None):
        import os, popen2, tempfile
        filename = tempfile.mktemp()
        fd = open(filename, "wc")
        fd.write(xml)
        fd.close()
        cmd = "xmllint --noout %s" % filename
        stdout, stdin, stderr = popen2.popen3(cmd)
        result = stderr.read()
        if not result.strip() == '':
            if page_id:
                raise AssertionError("%s is not well-formed XML:\n\n%s"
                    % (page_id, result))
            else:
                raise AssertionError("not well-formed XML:\n\n%s" % result)
        os.unlink(filename)

    def isWellFormedXML(self, xml):
        import os, tempfile
        filename = tempfile.mktemp()
        fd = open(filename, "wc")
        fd.write(xml)
        fd.close()
        status = os.system("xmllint --noout %s" % filename)
        os.unlink(filename)
        return status == 0

    def assertValidHTML(self, html, page_id=None):
        import os, popen2, tempfile
        filename = tempfile.mktemp()
        fd = open(filename, "wc")
        fd.write(html)
        fd.close()
        cmd = "xmllint --valid --html --noout %s" % filename
        stdout, stdin, stderr = popen2.popen3(cmd)
        result = stderr.read()
        if not result.strip() == '':
            if page_id:
                raise AssertionError("%s is not valid HTML:\n\n%s"
                    % (page_id, result))
            else:
                raise AssertionError("not is not valid HTML:\n\n%s" % result)
        os.unlink(filename)

    def assertValidXHTML(self, html, page_id=None):
        import os, popen2, tempfile
        filename = tempfile.mktemp()
        fd = open(filename, "wc")
        fd.write(html)
        fd.close()
        cmd = "xmllint --valid --noout %s" % filename
        stdout, stdin, stderr = popen2.popen3(cmd)
        result = stderr.read()
        if not result.strip() == '':
            if page_id:
                raise AssertionError("%s is not valid XHTML:\n\n%s"
                    % (page_id, result))
            else:
                raise AssertionError("not is not valid XHTML:\n\n%s" % result)
        os.unlink(filename)

    # XXX: unfortunately, the W3C checker sometime fails for no apparent
    # reason.
    def isValidCSS(self, css):
        """Check if <css> is valid CSS2 using W3C css-checker"""

        import urllib2, urllib, re
        CHECKER_URL = 'http://jigsaw.w3.org/css-validator/validator'
        data = urllib.urlencode({
            'text': css,
            'warning': '1',
            'profile': 'css2',
            'usermedium': 'all',
        })
        url = urllib2.urlopen(CHECKER_URL + '?' + data)
        result = url.read()

        is_valid = not re.search('<div id="errors">', result)
        # debug
        if not is_valid:
            print result
        return is_valid


##################################################

# The following BBB are for old code still importing these names.

def setupPortal(*args, **kw):
    import warnings
    warnings.warn("setupPortal shouldn't be used anymore.",
                  DeprecationWarning, stacklevel=2)

class CPSInstaller(object):
    pass
