#
# CPSTestCase
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('BTreeFolder2', quiet=1)
ZopeTestCase.installProduct('CMFCalendar', quiet=1)
ZopeTestCase.installProduct('CMFCore', quiet=1)
ZopeTestCase.installProduct('CMFDefault', quiet=1)
ZopeTestCase.installProduct('CMFTopic', quiet=1)
ZopeTestCase.installProduct('DCWorkflow', quiet=1)
ZopeTestCase.installProduct('Localizer', quiet=1)
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('CPSCore', quiet=1)
ZopeTestCase.installProduct('CPSDefault', quiet=1)
ZopeTestCase.installProduct('CPSDirectory', quiet=1)
ZopeTestCase.installProduct('NuxMetaDirectories', quiet=1)
ZopeTestCase.installProduct('NuxUserGroups', quiet=1)
ZopeTestCase.installProduct('TranslationService', quiet=1)

# XXX: these products should (and used to be) be optional, but they aren't
# right now.
ZopeTestCase.installProduct('CPSForum', quiet=1)
ZopeTestCase.installProduct('CPSSchemas', quiet=1)
ZopeTestCase.installProduct('CPSDocument', quiet=1)
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('Epoz', quiet=1)

# Optional products
try: ZopeTestCase.installProduct('CPSRSS', quiet=1)
except: pass
try: ZopeTestCase.installProduct('CPSChat', quiet=1)
except: pass
try: ZopeTestCase.installProduct('CPSCalendar', quiet=1)
except: pass
try: ZopeTestCase.installProduct('CPSMailingLists', quiet=1)
except: pass
try: ZopeTestCase.installProduct('CPSCollector', quiet=1)
except: pass

from AccessControl.SecurityManagement \
    import newSecurityManager, noSecurityManager

import time

# The folowing are patches needed because Localizer doesn't work
# well within ZTC

# This one is needed by ProxyTool.
def get_selected_language(self):
    """ """
    return self._default_language

from Products.Localizer.Localizer import Localizer
Localizer.get_selected_language = get_selected_language

# Dummy portal_catalog.

from OFS.SimpleItem import SimpleItem
class DummyTranslationService(SimpleItem):
    meta_type = 'Translation Service'
    id = 'translation_service'
    def translate(self, domain, msgid, *args, **kw):
        return msgid

# Dummy MessageCatalog
class DummyMessageCatalog:
    def __call__(self, message, *args, **kw):
        return message

    def get_selected_language(self):
        "xxx"
        return 'fr'

    def get_languages(self):
        return ['en', 'fr']

    def manage_import(self, *args, **kw):
        pass


from StringIO import StringIO
from Products.Localizer import LocalizerStringIO
from types import StringType, UnicodeType
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
    pass


class CPSInstaller:
    def __init__(self, app, quiet=0):
        if not quiet: 
            ZopeTestCase._print('Adding Portal Site ... ')
        self.app = app
        self._start = time.time()
        self._quiet = quiet

    def install(self, portal_id):
        self.addUser()
        self.login()
        self.addPortal(portal_id)
        self.fixupTranslationServices(portal_id)
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
            root_password1="passwd", root_password2="passwd",
            langs_list=['en'])

    # Change translation_service to DummyTranslationService
    def fixupTranslationServices(self, portal_id):
        portal = getattr(self.app, portal_id)
        portal.translation_service = DummyTranslationService()
        localizer = portal.Localizer
        for domain in localizer.objectIds():
            setattr(localizer, domain, DummyMessageCatalog())

    def logout(self):
        noSecurityManager()
        get_transaction().commit()
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

def setupPortal(PortalInstaller=CPSInstaller):
    # Create a CPS site in the test (demo-) storage
    app = ZopeTestCase.app()
    # PortalTestCase expects object to be called "portal", not "cps"
    if not hasattr(app, 'portal'):
        PortalInstaller(app).install('portal')
    ZopeTestCase.close(app)


