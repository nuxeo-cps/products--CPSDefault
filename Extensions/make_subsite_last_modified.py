from DateTime.DateTime import DateTime
from Products.CPSUtil.conflictresolvers import IncreasingDateTime
from Products.CPSDefault.voidresponses import SUBSITE_LAST_MODIFIED_DATE

def make(self):
    if self.hasObject(SUBSITE_LAST_MODIFIED_DATE):
        lmd = self[SUBSITE_LAST_MODIFIED_DATE]
    else:
        lmd = IncreasingDateTime(SUBSITE_LAST_MODIFIED_DATE)
        self._setObject(SUBSITE_LAST_MODIFIED_DATE, lmd)
    lmd.set(DateTime())
