##parameters=obj=None, utool=None, concat=0
# $Id$
# return the minimal url to access the object ex: /, /cps/foo
#  if concat=1 there is no trailing '/' ex: '', /cps/foo and
if not utool:
    utool = context.portal_url
base_url = context.getBaseUrl(utool=utool)

if not obj:
    obj = context

if obj.meta_type == 'CMF Catalog' and hasattr(obj, 'getObject'):
    obj = obj.getObject()

context_url = base_url + utool.getRelativeUrl(obj)
if concat and context_url[-1] == '/':
    context_url = context_url[:-1]


return context_url
