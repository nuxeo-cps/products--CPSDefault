##parameters=utool=None
# $Id$
# return the base url of the cps server, ex: /cps/ or /
if not utool:
    utool = context.portal_url
rurl = utool(relative=1)
cps_folder = context.getPhysicalPath()[1]
base_url = '/'
if rurl.startswith(cps_folder):
    base_url += cps_folder + '/'

return base_url
