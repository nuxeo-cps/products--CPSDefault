#
# CPSTestCase
#

from Testing import ZopeTestCase

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

# Patch Localizer, it doesn't want to work within the test
# harness.
def get_selected_language(self):
    """ """
    return self._default_language


from Products.Localizer.Localizer import Localizer
Localizer.get_selected_language = get_selected_language

from AccessControl.SecurityManagement \
    import newSecurityManager, noSecurityManager
from AccessControl.User import User

from Acquisition import aq_base
import time


class CPSTestCase(ZopeTestCase.PortalTestCase):
    pass


class PortalInstaller:
    def __init__(self, app, id, quiet=0):
        self.app = app
        self._start = time.time()

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

    def logout(self):
        noSecurityManager()
        get_transaction().commit()
        if not quiet: 
            ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


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

def setupPortal():
    # Create a CPS site in the test (demo-) storage
    app = ZopeTestCase.app()
    # PortalTestCase expects object to be called "portal", not "cps"
    PortalInstaller(app).install('portal')
    ZopeTestCase.close(app)

