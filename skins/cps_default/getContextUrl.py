## Script (Python) "getPortalUrl"
##parameters=
# $Id$
utool = context.portal_url
rurl = utool(relative=1)    # browser relative url
cps_folder = context.getPhysicalPath()[1]
cps_url = '/'
if rurl.startswith(cps_folder):
    cps_url += cps_folder + '/'
return cps_url + utool.getRelativeUrl(context)
