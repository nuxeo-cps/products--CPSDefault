##parameters=utool=None
# $Id$
"""
DO NOT USE THIS DEPRECATED SCRIPT, QUERY URL TOOL INSTEAD:
context.portal_url.getBaseUrl()


Return the base url of the cps server, ex: /cps/ or /
Deal with virtual hosting
"""

from zLOG import LOG, DEBUG
from Products.CMFCore.utils import getToolByName

if utool is None:
    utool = getToolByName(context, 'portal_url')

if hasattr(utool.aq_inner.aq_explicit, 'getBaseUrl'):
    base_url = utool.getBaseUrl()
else:
    # backward compatibility
    portal = utool.getPortalObject()
    base_url = portal.absolute_url_path()
    if not base_url.endswith('/'):
        base_url += '/'

return base_url
