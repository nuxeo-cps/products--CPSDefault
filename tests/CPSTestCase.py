# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Stefane Fermigier <sf@nuxeo.com>
# M.-A. Darche
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
import re
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
ZopeTestCase.installProduct('CPSRemoteController', quiet=1)
ZopeTestCase.installProduct('CPSCollector', quiet=1)

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

# DOTALL: Make the "." special character match any character at all,
# including a newline; without this flag, "." will match anything except a
# newline.
#
# For example:
#
# <div id="errors">
# rrrrrrrRRRRRR
# </div>
# <div id="warnings">
# Hummmmmmmmmmm
# </div>
# <div id="css">
# </div>
#
# makes it possible to retrieve both
# "rrrrrrrRRRRRR" and "Hummmmmmmmmmm"
#
CSS_VALIDATOR_ERRORS_REGEXP = re.compile(
    u'<div id="errors">(.*)</div>.*?<div id="warnings">(.*)</div>.*?<div id="css">',
    re.DOTALL)


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
        fd, file_path = tempfile.mkstemp()
        f = os.fdopen(fd, 'wc')
        f.write(xml)
        f.close()
        cmd = "xmllint --noout %s" % file_path
        stdout, stdin, stderr = popen2.popen3(cmd)
        result = stderr.read()
        if not result.strip() == '':
            if page_id:
                raise AssertionError("%s is not well-formed XML:\n\n%s"
                    % (page_id, result))
            else:
                raise AssertionError("not well-formed XML:\n\n%s" % result)
        os.remove(file_path)

    def isWellFormedXML(self, xml):
        import os, tempfile
        fd, file_path = tempfile.mkstemp()
        f = os.fdopen(fd, 'wc')
        f.write(xml)
        f.close()
        status = os.system("xmllint --noout %s" % file_path)
        os.remove(file_path)
        return status == 0

    def assertValidHTML(self, html, page_id=None):
        import os, popen2, tempfile
        fd, file_path = tempfile.mkstemp()
        f = os.fdopen(fd, 'wc')
        f.write(html)
        f.close()
        cmd = "xmllint --valid --html --noout %s" % file_path
        stdout, stdin, stderr = popen2.popen3(cmd)
        result = stderr.read()
        if not result.strip() == '':
            if page_id:
                raise AssertionError("%s is not valid HTML:\n%s"
                    % (page_id, result))
            else:
                raise AssertionError("Invalid HTML:\n%s" % result)
        os.remove(file_path)

    def assertValidXHTML(self, html, page_id=None):
        import os, popen2, tempfile
        fd, file_path = tempfile.mkstemp()
        f = os.fdopen(fd, 'wc')
        f.write(html)
        f.close()
        cmd = "xmllint --valid --noout %s" % file_path
        stdout, stdin, stderr = popen2.popen3(cmd)
        result = stderr.read()
        if not result.strip() == '':
            if page_id:
                raise AssertionError("%s is not valid XHTML:\n%s"
                    % (page_id, result))
            else:
                raise AssertionError("Invalid XHTML:\n%s" % result)
        os.remove(file_path)

    def assertValidCss(self, css, ressource_name='', css_profile='css21',
                       input_format='css',
                       fail_on_warnings=False):
        """Check if <css> is valid CSS using the W3C CSS validator.
        """
        is_valid, errors = self.isValidCss(css, css_profile, input_format,
                                           fail_on_warnings)
        if not is_valid:
            raise AssertionError("%s is or contains invalid CSS:\n%s"
                                 % (ressource_name, errors))

    def isValidCss(self, css, css_profile='css21',
                   input_format='css',
                   fail_on_warnings=False):
        """Check if <css> is valid CSS using the W3C CSS validator and return
        the errors found if any.

        input_format can be either "css", "html" or "xml".

        The test is done using a local css validator if one is present.
        """
        is_valid = True
        errors = ""
        # Version using the online W3C CSS validator.
        # Using the online W3C CSS validator should be avoided since it may be
        # off-line for maintainance or refusing too close connexions to avoid
        # DOS situations.
        #import urllib2, urllib, re
        #CHECKER_URL = 'http://jigsaw.w3.org/css-validator/validator'
        #data = urllib.urlencode({
        #    'text': css,
        #    'warning': '1',
        #    'profile': css_profile,
        #    'usermedium': 'all',
        #})
        #url = urllib2.urlopen(CHECKER_URL + '?' + data)
        #result = url.read()

        try:
            java_binary_path = self.getBinaryPath('java')
        except Exception, exception:
            print "isValidCSS: %s" % str(exception)
            return is_valid, errors
        import os, popen2, tempfile
        # It is required that the file passed to the validator has a file
        # suffix corresponding to its content type since the command line
        # interface of the validator uses this to decide how to process the
        # file.
        suffix = '.' + input_format
        fd, file_path = tempfile.mkstemp(suffix)
        f = os.fdopen(fd, 'wc')
        f.write(css)
        f.close()
        css_validator_jar_path = '/usr/local/share/java/css-validator.jar'
        if not os.access(css_validator_jar_path, os.R_OK):
            print ("isValidCSS: %s not present or not readable "
                   "=> no CSS validation occured" % css_validator_jar_path)
            return is_valid, errors
        cmd = ('%s -jar %s -html -%s %s'
               % (java_binary_path, css_validator_jar_path,
                  css_profile, file_path))
        stdout, stdin, stderr = popen2.popen3(cmd)
        result = stdout.read()
        os.remove(file_path)
        match = CSS_VALIDATOR_ERRORS_REGEXP.search(result)
        is_valid = not match
        if not is_valid:
            errors = match.group(1)
        return is_valid, errors

    class MissingBinary(Exception): pass

    def getBinaryPath(self, binary_name):
        """Return the path for the given binary if it can be found and if it is
        executable.
        """
        binary_search_path = [
            '/usr/local/bin',
            '/bin',
            '/usr/bin',
        ]
        binary_path = None
        mode   = os.R_OK | os.X_OK
        for p in binary_search_path:
            path = os.path.join(p, binary_name)
            if os.access(path, mode):
                binary_path = path
                break
        else:
            raise MissingBinary('Unable to find binary "%s"' % binary_name)
        return binary_path

##################################################

# The following BBB are for old code still importing these names.

def setupPortal(*args, **kw):
    import warnings
    warnings.warn("setupPortal shouldn't be used anymore.",
                  DeprecationWarning, stacklevel=2)

class CPSInstaller(object):
    pass
