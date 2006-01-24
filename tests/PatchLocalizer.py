# The following are patches needed because Localizer doesn't work well within
# ZopeTestCase (request and encoding related issues)

from Products.Localizer.Localizer import Localizer

# session related problem
def get_selected_language(self):
    """ """
    return self._default_language

# Localizer is present
Localizer.get_selected_language = get_selected_language

# LocalizerStringIO
from StringIO import StringIO
from Products.Localizer import LocalizerStringIO

# Un-patch LocalizerStringIO
def LocalizerStringIO_write(self, s):
    StringIO.write(self, s)
LocalizerStringIO.write = LocalizerStringIO_write

# Hack around Unicode problem
def LocalizerStringIO_getvalue(self):
    if self.buflist:
        for buf in self.buflist:
            if isinstance(buf, unicode):
                self.buf += buf.encode('latin-1')
            else:
                self.buf += buf
        self.buflist = []
    return self.buf

LocalizerStringIO.getvalue = LocalizerStringIO_getvalue

