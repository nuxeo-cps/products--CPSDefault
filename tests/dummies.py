# Dummy objects (TranslationService and MessageCatalogs) for testing

# XXX: this has been copied verbatim from CPSSkis/tests/TestUtil.py

import os

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem

target = os.environ.get('CPSSKINS_TARGET', 'CMF')

##########################################
try:
    from Products.Localizer.Localizer import Localizer
except ImportError:
    pass
else:

    # This one is needed by ProxyTool.
    def get_selected_language(self):
        """ """
        return self._default_language

    # Localizer is present
    Localizer.get_selected_language = get_selected_language

    # LocalizerStringIO
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

##########################################
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

##########################################
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

##########################################
from Products.CPSSkins.PortalThemesTool import PortalThemesTool

# session management
def setViewMode(self, **kw):
    """ """
    self.fake_session = {}
    self.fake_session.update(kw)

def getViewMode(self):
    """ """
    return getattr(self, 'fake_session', {})

PortalThemesTool.setViewMode = setViewMode
PortalThemesTool.getViewMode = getViewMode

##########################################

if target == 'CPS3':

    from Products.CPSPortlets.PortletsTool import PortletsTool

    # disable CPSPortlets events
    def notify_event(self, event_type, object, infos):
        pass

    PortletsTool.notify_event = notify_event

##########################################
