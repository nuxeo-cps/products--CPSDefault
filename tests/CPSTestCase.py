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
import sys
import re
import time
import transaction
from Testing import ZopeTestCase
from Testing.ZopeTestCase.functional import ResponseWrapper
from zope.app.publication.interfaces import BeforeTraverseEvent
from zope.app.component.site import threadSiteSubscriber
from zope.app.testing.functional import ZCMLLayer
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CPSUtil.testing.introspect import ZOPE_VERSION
from Products.CPSCore.EventServiceTool import SubscriberDef

ZopeTestCase.installProduct('ZCTextIndex', quiet=1)
ZopeTestCase.installProduct('BTreeFolder2', quiet=1)
ZopeTestCase.installProduct('StandardCacheManagers', quiet=1)
ZopeTestCase.installProduct('SiteAccess', quiet=1)
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('UnicodeLexicon', quiet=1)
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
ZopeTestCase.installProduct('CPSDesignerThemes', quiet=1)
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

config_file = 'cpsdefaultlayer-zope-%d.%d.zcml' % ZOPE_VERSION[:2]
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

from Products.CMFCore.utils import SimpleItemWithProperties
class EventRecorder(SimpleItemWithProperties):
    def __init__(self, id):
        self._setId(id)
        # Using a volatile variable for not having commit hoops
        # in functional tests, see #1848.
        self._v_events = []

    def notify_event(self, *args):
        if getattr(self, '_v_events', None) is None:
            self._v_events = []
        self._v_events.append(args)

    def clear(self):
        self._v_events = []

    def getRecords(self):
        return self._v_events

def ensure_site_manager(obj):
        """If obj should have a local site manager, enables it.

        This is done by simulating a Z3 traversal, since zope changes the
        current thread-local site manager this way.
        """
        request = object()
        ev = BeforeTraverseEvent(obj, request)
        threadSiteSubscriber(obj, ev)

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

        # the crash shield doesn't help understanding what's wrong in a test
        getToolByName(self.portal, 'portal_cpsportlets').shield_disabled = True

        self.addEventRecorder()
        self.logout()
        transaction.commit()

    def addRootUser(self):
        aclu = self.app.acl_users
        aclu._doAddUser('CPSTestCase', '', ['Manager'], [])

    def addEventRecorder(self):
        sid = 'event_recorder'
        self.portal._setObject(sid, EventRecorder(sid))
        sdef = SubscriberDef(sid)
        sdef.manage_changeProperties(subscriber=sid,
                                       action='event',
                                       meta_type='*',
                                       notification_type='synchronous',
                                       compressed=False,
                                       activated=True)
        self.portal.portal_eventservice._setObject(sid, sdef)

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
        self.portal = getattr(self.app, PORTAL_ID)
        ensure_site_manager(self.portal)
        self.login()
        tool = getToolByName(self.portal, 'portal_setup')
        for extension_id in self.extension_ids:
            tool.runAllImportStepsFromProfile('profile-%s' % extension_id)
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
        self.portal.changeSkin('CPSSkins', self.app.REQUEST)

        ensure_site_manager(self.portal) # wiped during tear down

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

    def zopePublish(self, path, basic=None, env=None, extra=None,
                request_method='GET', stdin=None, handle_errors=True):
        """Derived from FunctionalTestCase but doesn't commit any transaction.

        FunctionalTestCase subclasses sandbox.sandboxed and its publish()
        method starts by committing the transaction.
        At the time of this writing, the impact of all of this is not really
        clear, but it's possible that the sandbox defeates the layer
        factorization, and/or that the commit is unwanted.
        We prefer to reimplement. Readapting just this once for later Zope
        versions is no high cost

        we don't use the savestate decorator either (restores site and
        security managers). Apart from that, this is a simle copy-paste.
        """

        from StringIO import StringIO
        from ZPublisher.Response import Response
        from ZPublisher.Test import publish_module

        # here was the transaction commit

        if env is None:
            env = {}
        if extra is None:
            extra = {}

        request = self.app.REQUEST

        env['SERVER_NAME'] = request['SERVER_NAME']
        env['SERVER_PORT'] = request['SERVER_PORT']
        env['REQUEST_METHOD'] = request_method

        p = path.split('?')
        if len(p) == 1:
            env['PATH_INFO'] = p[0]
        elif len(p) == 2:
            [env['PATH_INFO'], env['QUERY_STRING']] = p
        else:
            raise TypeError, ''

        if basic:
            env['HTTP_AUTHORIZATION'] = "Basic %s" % base64.encodestring(basic)

        if stdin is None:
            stdin = StringIO()

        outstream = StringIO()
        response = Response(stdout=outstream, stderr=sys.stderr)

        publish_module('Zope2',
                       response=response,
                       stdin=stdin,
                       environ=env,
                       extra=extra,
                       debug=not handle_errors,
                      )

        return ResponseWrapper(response, outstream, path)


class CPSPermWorkflowTestCase(CPSTestCase):
    """A subclass providing workflow and permissons related assertions."""

    def afterSetUp(self):
        CPSTestCase.afterSetUp(self)
        self.wftool = self.portal.portal_workflow

    def assertPerm(self, perm, ob, user_id=None):
        if user_id is not None:
            old_user = getSecurityManager().getUser().getId()
            self.login(user_id)
        if not _checkPermission(perm, ob):
            self.fail("Don't have %s permission on %s" % (perm, ob))
        if user_id is not None:
            self.login(old_user)

    def assertNotPerm(self, perm, ob, user_id=None):
        if user_id is not None:
            old_user = getSecurityManager().getUser().getId()
            self.login(user_id)
        if _checkPermission(perm, ob):
            self.fail("Should not have %s permission on %s" % (perm, ob))
        if user_id is not None:
            self.login(old_user)

    failIfPerm = assertNotPerm
    failIfNotPerm = assertPerm

    def assertReviewState(self, ob, state):
        self.assertEquals(self.wftool.getInfoFor(ob, 'review_state'),
                          state)

    def assertCreationUIProposed(self, container, ptype):
        ftis = [fti.getId() for fti in container.getSortedContentTypes()]
        if ptype in ftis:
            return
        self.fail("portal_type '%s' not in %s" % (ptype, ftis))

    def currentUser(self):
        return getSecurityManager().getUser()


##################################################

# The following BBB are for old code still importing these names.

def setupPortal(*args, **kw):
    import warnings
    warnings.warn("setupPortal shouldn't be used anymore.",
                  DeprecationWarning, stacklevel=2)

class CPSInstaller(object):
    pass
