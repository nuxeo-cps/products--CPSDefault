#
# CPSTestCase
#

from Testing import ZopeTestCase

ZopeTestCase.installProduct('BTreeFolder2')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('CPSCore')
ZopeTestCase.installProduct('CPSDefault')
ZopeTestCase.installProduct('NuxMetaDirectories')
ZopeTestCase.installProduct('NuxUserGroups')
ZopeTestCase.installProduct('TranslationService')
#
ZopeTestCase.installProduct('CPSForum')
ZopeTestCase.installProduct('CPSSchemas')
ZopeTestCase.installProduct('CPSDocument')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Epoz')

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

# Un-patch LocalizerStringIO

from StringIO import StringIO
from Products.Localizer import LocalizerStringIO
def LocalizerStringIO_write(self, s):
    # Don't write anything
    StringIO.write(self, "")
LocalizerStringIO.write = LocalizerStringIO_write


class CPSTestCase(ZopeTestCase.PortalTestCase):
    pass


class CPSInstaller:
    def __init__(self, app, quiet=0):
        if not quiet: 
            ZopeTestCase._print('Adding Portal Site ... ')
        self.app = app
        self._start = time.time()
        self._quiet = quiet

    def install(self, id):
        self.addUser()
        self.login()
        self.addPortal(id)
        self.logout()

    def addUser(self):
        uf = self.app.acl_users
        uf._doAddUser('CPSTestCase', '', ['Manager'], [])

    def login(self):
        uf = self.app.acl_users
        user = uf.getUserById('CPSTestCase').__of__(uf)
        newSecurityManager(None, user)

    def addPortal(self, id):
        factory = self.app.manage_addProduct['CPSDefault']
        factory.manage_addCPSDefaultSite(id, 
            root_password1="passwd", root_password2="passwd",
            langs_list=['en'])

        # Change translation_service to DummyTranslationService
        portal = getattr(self.app, id)
        assert portal.translation_service
        portal.translation_service = DummyTranslationService()

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


