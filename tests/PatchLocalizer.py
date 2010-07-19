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
from TAL.TALInterpreter import FasterStringIO
from Products.Localizer import LocalizerStringIO

# Un-patch LocalizerStringIO
def LocalizerStringIO_write(self, s):
    FasterStringIO.write(self, s)
LocalizerStringIO.write = LocalizerStringIO_write


