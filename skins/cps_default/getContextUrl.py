## Script (Python) "getPortalUrl"
##parameters=
# $Id$
rurl = context.portal_url(relative=1)
rurl = rurl and '/' + rurl or ''

return rurl
