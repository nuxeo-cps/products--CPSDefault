##parameters=content_url
# $Id$
"""Removes the reference to an archived version if there is one present.
"""

from Products.CPSDefault.utils import getNonArchivedVersionContextUrl

return getNonArchivedVersionContextUrl(content_url)
