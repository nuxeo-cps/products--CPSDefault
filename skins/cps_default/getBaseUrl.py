##parameters=utool=None
# $Id$
"""
Return the base url of the cps server, ex: /cps/ or /
Deal with virtual hosting

XXX AT: this is now a method of portal_url, this script is here only for
compatibility reasons.
"""

from zLOG import LOG, DEBUG
from Products.CMFCore.utils import getToolByName

if utool is None:
    utool = getToolByName(context, 'portal_url')

base_url = utool.getBaseURL()

return base_url
