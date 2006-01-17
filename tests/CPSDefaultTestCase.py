import warnings
warnings.warn("CPSDefaultTestCase is deprecated, use CPSTestCase instead.",
              DeprecationWarning, stacklevel=2)

from Products.CPSDefault.tests.CPSTestCase import (
    CPSTestCase as CPSDefaultTestCase)
