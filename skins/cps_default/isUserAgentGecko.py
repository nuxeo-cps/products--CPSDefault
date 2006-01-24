##parameters=REQUEST=None
# $Id$
"""A skin script to be able to call isUserAgentGecko from DTML.
"""
from Products.CPSUtil.integration import isUserAgentGecko

return isUserAgentGecko(REQUEST)

