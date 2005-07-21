##parameters=utool=None
# $Id$
"""
DO NOT USE THIS DEPRECATED SCRIPT, QUERY URL TOOL INSTEAD:
context.portal_url.getBaseURL()


Return the base url of the cps server, ex: /cps/ or /
Deal with virtual hosting
"""

from zLOG import LOG, DEBUG
from Products.CMFCore.utils import getToolByName

if utool is None:
    utool = getToolByName(context, 'portal_url')

base_url = utool.getBaseURL()

return base_url
