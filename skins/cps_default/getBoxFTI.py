##parameters=
# $Id$
"""
Return the boxes Factory type information.
"""

types = context.portal_types.listTypeInfo()

boxestypes = [x for x in types 
                if hasattr(x, 'cps_is_portalbox') and x.cps_is_portalbox]

return boxestypes
