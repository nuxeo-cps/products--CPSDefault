## Script (Python) "getPortalUrl"
##parameters=obj=None, utool=None
# $Id$
# return the minimal url to access the object ex: /cps/foo
if not utool:
    utool=context.portal_url
base_url=context.getBaseUrl(utool=utool)
if not obj:
    obj = context
    
return base_url + utool.getRelativeUrl(obj)
