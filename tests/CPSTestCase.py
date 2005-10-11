#
# CPSTestCase
#

import os, tempfile
import zLOG
from Testing import ZopeTestCase
import Products

ZopeTestCase.installProduct('ZCTextIndex', quiet=1)
ZopeTestCase.installProduct('BTreeFolder2', quiet=1)
ZopeTestCase.installProduct('CMFCalendar', quiet=1)
ZopeTestCase.installProduct('CMFCore', quiet=1)
ZopeTestCase.installProduct('CMFDefault', quiet=1)
ZopeTestCase.installProduct('CMFTopic', quiet=1)
ZopeTestCase.installProduct('CMFSetup', quiet=1)
ZopeTestCase.installProduct('DCWorkflow', quiet=1)
ZopeTestCase.installProduct('Localizer', quiet=1)
ZopeTestCase.installProduct('CPSBoxes', quiet=0)
ZopeTestCase.installProduct('CPSPortlets', quiet=0)
ZopeTestCase.installProduct('CPSNavigation', quiet=0)
ZopeTestCase.installProduct('CPSRSS', quiet=1)
ZopeTestCase.installProduct('CPSCore', quiet=1)
ZopeTestCase.installProduct('CPSWorkflow', quiet=1)
ZopeTestCase.installProduct('CPSDefault', quiet=1)
ZopeTestCase.installProduct('CPSDirectory', quiet=1)
ZopeTestCase.installProduct('CPSUserFolder', quiet=1)
ZopeTestCase.installProduct('CPSForum', quiet=1)
ZopeTestCase.installProduct('CPSSchemas', quiet=1)
ZopeTestCase.installProduct('CPSDocument', quiet=1)
ZopeTestCase.installProduct('CPSOOo', quiet=1)
ZopeTestCase.installProduct('Epoz', quiet=1)
ZopeTestCase.installProduct('CPSSkins', quiet=1)
ZopeTestCase.installProduct('TranslationService', quiet=1)
ZopeTestCase.installProduct('SiteAccess', quiet=1)
ZopeTestCase.installProduct('MailHost', quiet=1)

# XXX: these products should (and used to be) be optional, but they aren't
# right now.
ZopeTestCase.installProduct('CPSSubscriptions', quiet=1)
ZopeTestCase.installProduct('CPSNewsLetters', quiet=1)
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('CPSWiki', quiet=1)

# Five is optional, but if they exist they must be installed for tests
# to run properly.
ZopeTestCase.installProduct('Five', quiet=1)
ZopeTestCase.installProduct('CMFonFive', quiet=1)
ZopeTestCase.installProduct('CPSSharedCalendar', quiet=1)

try:
    import transaction
except ImportError:
    # BBB: for Zope 2.7
    from Products.CMFCore.utils import transaction



PORTAL_ID = 'portal'
MANAGER_ID = 'manager'
MANAGER_EMAIL = 'webmaster@localhost'
MANAGER_PASSWORD = 'passwd'

# Optional products
for product in ('CPSChat', 'CPSCalendar', 'CPSCollector',
        'CPSMailBoxer'):
    try:
        ZopeTestCase.installProduct(product, quiet=1)
    except:
        pass

test_cpsskins = (os.environ.get('CPSSKINS_TARGET', '') == 'CPS3')
if test_cpsskins:
    try:
        ZopeTestCase.installProduct('CPSSkins', quiet=1)
        import Products.CPSSkins
    except ImportError:
        test_cpsskins = False

from AccessControl.SecurityManagement \
    import newSecurityManager, noSecurityManager
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

import time

# The folowing are patches needed because Localizer doesn't work
# well within ZTC

# This one is needed by ProxyTool.
def get_selected_language(self):
    """ """
    return self._default_language


from Products.Localizer.Localizer import Localizer
Localizer.get_selected_language = get_selected_language

from OFS.SimpleItem import SimpleItem
class DummyTranslationService(SimpleItem):
    meta_type = 'Translation Service'
    id = 'translation_service'

    def translate(self, domain, msgid, *args, **kw):
        return msgid

    def translateDefault(self, msgid, target_language, *args, **kw):
        if msgid == 'words_meaningless' and target_language == 'en':
            msgstr = "a the this these those of am is are has have or and i maybe perhaps"
        elif msgid == 'words_meaningless' and target_language == 'fr':
            msgstr = "et ou un une le la les l de des ces que qui est sont a ont je voici"
        else:
            msgstr = msgid
        return msgstr

    def __call__(self, *args, **kw):
        return self.translate('default', *args, **kw)

    def getDomainInfo(self):
        return [(None, 'Localizer/default')]

    def manage_addDomainInfo(self, domain, path, REQUEST=None, **kw):
        pass

    def getDefaultLanguage(self):
        return 'en'

    def getSelectedLanguage(self):
        return 'en'

    def getSupportedLanguages(self):
        return ['en', 'fr', 'de']

class DummyMessageCatalog(SimpleItem):
    security = ClassSecurityInfo()
    def __call__(self, message, *args, **kw):
        #return self.gettext(self, message, lang, args, kw)
        return message

    security.declarePublic('gettext')
    def gettext(self, message, lang=None, *args, **kw):
        if message == 'words_meaningless' and lang == 'en':
            message = "a the this these those of am is are has have or and i maybe perhaps"
        elif message == 'words_meaningless' and lang == 'fr':
            message = "un une le la les l de des ces est sont a ont ou et je voici"
        return message

    def get_selected_language(self):
        "xxx"
        return 'fr'

    def get_languages(self):
        return ['en', 'fr', 'de']

    def manage_import(self, *args, **kw):
        pass

    def wl_isLocked(self):
        return None # = False

InitializeClass(DummyMessageCatalog)


from StringIO import StringIO
from Products.Localizer import LocalizerStringIO
from types import UnicodeType
# Un-patch LocalizerStringIO
def LocalizerStringIO_write(self, s):
    StringIO.write(self, s)
# Hack around Unicode problem
def LocalizerStringIO_getvalue(self):
    if self.buflist:
        for buf in self.buflist:
            if type(buf) == UnicodeType:
                self.buf += buf.encode('latin-1')
            else:
                self.buf += buf
        self.buflist = []
    return self.buf
LocalizerStringIO.write = LocalizerStringIO_write
LocalizerStringIO.getvalue = LocalizerStringIO_getvalue

class CPSTestCase(ZopeTestCase.PortalTestCase):

    # Override _setup, setUp is not supposed to be overriden
    def _setup(self):

        ZopeTestCase.PortalTestCase._setup(self)

        # Some skins need sessions (not sure if it's a good thing).
        # Localizer too.
        # Both lines below are needed.
        SESSION = {}
        self.portal.REQUEST['SESSION'] = SESSION
        self.portal.REQUEST.SESSION = SESSION

    def printLogErrors(self, min_severity=zLOG.INFO):
        """Print out the log output on the console.
        """
        if hasattr(zLOG, 'old_log_write'):
            return
        def log_write(subsystem, severity, summary, detail, error,
                      PROBLEM=zLOG.PROBLEM, min_severity=min_severity):
            if severity >= min_severity:
                print "%s(%s): %s %s" % (subsystem, severity, summary, detail)
        zLOG.old_log_write = zLOG.log_write
        zLOG.log_write = log_write

    def isValidXML(self, xml):
        filename = tempfile.mktemp()
        fd = open(filename, "wc")
        fd.write(xml)
        fd.close()
        status = os.system("xmllint --noout %s" % filename)
        os.unlink(filename)
        return status == 0

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


class CPSInstaller:
    def __init__(self, app, quiet=0):
        if not quiet:
            ZopeTestCase._print('Adding Portal Site ... ')
        self.app = app
        self._start = time.time()
        self._quiet = quiet

    def install(self, portal_id):

        # During setup and tests we want synchronous indexing.
        from Products.CPSCore.IndexationManager import get_indexation_manager
        from Products.CPSCore.IndexationManager import IndexationManager
        IndexationManager.DEFAULT_SYNC = True # Monkey patch
        get_indexation_manager().setSynchronous(True) # Current transaction

        # During setup and tests we want synchronous tree cache updates
        from Products.CPSCore.TreeCacheManager import get_treecache_manager
        from Products.CPSCore.TreeCacheManager import TreeCacheManager
        TreeCacheManager.DEFAULT_SYNC = True # Monkey patch
        get_treecache_manager().setSynchronous(True) # current transaction

        self.addUser()
        self.login()
        self.addPortal(portal_id)
        self.fixupTranslationServices(portal_id)
        if test_cpsskins:
            self.setupCPSSkins(portal_id)
        self.logout()

    def addUser(self):
        uf = self.app.acl_users
        uf._doAddUser('CPSTestCase', '', ['Manager'], [])

    def login(self):
        uf = self.app.acl_users
        user = uf.getUserById('CPSTestCase').__of__(uf)
        newSecurityManager(None, user)

    def addPortal(self, portal_id):
        factory = self.app.manage_addProduct['CPSDefault']
        factory.manage_addCPSDefaultSite(portal_id,
                                         langs_list=['en', 'fr', 'de'],
                                         manager_id=MANAGER_ID,
                                         manager_email=MANAGER_EMAIL,
                                         manager_password=MANAGER_PASSWORD,
                                         manager_password_confirmation=MANAGER_PASSWORD,
                                         )

    # Change translation_service to DummyTranslationService
    def fixupTranslationServices(self, portal_id):
        portal = getattr(self.app, portal_id)
        # XXX don't know why we use a fake translation service
        # we only need to add getSelectedLanguage and getLanguage methods
        # to TranslationService.Domain.DummyDomain to use the real one
        portal.translation_service = DummyTranslationService()
        localizer = portal.Localizer
        for domain in localizer.objectIds():
            setattr(localizer, domain, DummyMessageCatalog())

    # This will go away when CPSSkins will get integrated in CPSDefault
    def setupCPSSkins(self, portal_id):
        portal = getattr(self.app, portal_id)
        factory = portal.manage_addProduct['CPSSkins']
        factory.manage_addCPSSkins(portal_id, SourceSkin='Basic',
             Target='CPS3', ReinstallDefaultThemes=1)

    def logout(self):
        noSecurityManager()
        transaction.commit()
        if not self._quiet:
            ZopeTestCase._print('done (%.3fs)\n'
                % (time.time() - self._start,))


def optimize():
    '''Significantly reduces portal creation time.'''
    def __init__(self, text):
        # Don't compile expressions on creation
        self.text = text
    from Products.CMFCore.Expression import Expression
    Expression.__init__ = __init__

    def _cloneActions(self):
        # Don't clone actions but convert to list only
        return list(self._actions)
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
    ActionProviderBase._cloneActions = _cloneActions

optimize()

class FakeErrorLog:
    def raising(self, *args):
        pass

##############################################################
##############################################################

def setupPortal(PortalInstaller=CPSInstaller):
    # Create a CPS site in the test (demo-) storage
    app = ZopeTestCase.app()

    # PortalTestCase expects object to be called "portal", not "cps"
    if hasattr(app, PORTAL_ID):
        app.manage_delObjects([PORTAL_ID])

    # Add an error_log (used by CMFQuickInstaller)
    app.error_log = FakeErrorLog()

    PortalInstaller(app).install(PORTAL_ID)
    ZopeTestCase.close(app)
