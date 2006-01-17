#
# CPSTestCase
#

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
ZopeTestCase.installProduct('CPSBoxes', quiet=1)
ZopeTestCase.installProduct('CPSPortlets', quiet=1)
ZopeTestCase.installProduct('CPSNavigation', quiet=1)
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
ZopeTestCase.installProduct('FCKeditor', quiet=1)
ZopeTestCase.installProduct('Epoz', quiet=1)
ZopeTestCase.installProduct('CPSSkins', quiet=1)
ZopeTestCase.installProduct('TranslationService', quiet=1)
ZopeTestCase.installProduct('SiteAccess', quiet=1)
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('ExternalEditor', quiet=1)
ZopeTestCase.installProduct('StandardCacheManagers', quiet=1)
ZopeTestCase.installProduct('Five', quiet=1)

# XXX: these products should (and used to be) be optional, but they aren't
# right now.
ZopeTestCase.installProduct('CPSSubscriptions', quiet=1)
ZopeTestCase.installProduct('CPSNewsLetters', quiet=1)
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('CPSWiki', quiet=1)


# The folowing are patches needed because Localizer doesn't work
# well within ZTC

# This one is needed by ProxyTool.
def get_selected_language(self):
    """ """
    return self._default_language

from Products.Localizer.Localizer import Localizer
Localizer.get_selected_language = get_selected_language


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

    layer = 'Products.CPSDefault.tests.CPSDefaultLayer.CPSDefaultLayer'

    # Override _setup, setUp is not supposed to be overriden
    def _setup(self):

        # FIXME: ugly hack, fixing something that is broken elsewhere
        members_directory = self.app.portal.portal_directories.members
        entries = members_directory._searchEntries()
        if 'test_user_1_' in entries:
            members_directory._delObject('test_user_1_')

        ZopeTestCase.PortalTestCase._setup(self)

        # Some skins need sessions (not sure if it's a good thing).
        # Localizer too.
        # Both lines below are needed.
        SESSION = {}
        self.portal.REQUEST['SESSION'] = SESSION
        self.portal.REQUEST.SESSION = SESSION

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

    def isValidXML(self, xml):
        import os
        import tempfile
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


##################################################

# The following BBB are for old code still importing these names.

def setupPortal(*args, **kw):
    import warnings
    warnings.warn("setupPortal shouldn't be used anymore.",
                  DeprecationWarning, stacklevel=2)

class CPSInstaller(object):
    pass

from Products.CPSDefault.tests.CPSDefaultLayer import PORTAL_ID
from Products.CPSDefault.tests.CPSDefaultLayer import MANAGER_ID
from Products.CPSDefault.tests.CPSDefaultLayer import MANAGER_EMAIL
from Products.CPSDefault.tests.CPSDefaultLayer import MANAGER_PASSWORD
