## Script (Python) "getBoxFTI"
##parameters=
# $Id$
"""Return the boxes Factory type information."""

types = context.portal_types.listTypeInfo()

boxestypes = [x for x in types if x.getActionById('isportalbox',None)]

return boxestypes
