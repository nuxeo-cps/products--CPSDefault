from Products.CPSUtil.conflictresolvers import IncreasingDateTime
from Products.CPSDefault.voidresponses import SUBSITE_LAST_MODIFIED_DATE

def make(self):
    lmd = IncreasingDateTime(SUBSITE_LAST_MODIFIED_DATE)
    self._setObject(SUBSITE_LAST_MODIFIED_DATE, lmd)
