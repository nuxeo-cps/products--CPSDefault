##parameters=obj=None, utool=None, concat=0
# $Id$
"""
Return the minimal url to access the object ex: /, /cps/foo

If concat=1 there is no trailing '/' ex: '', /cps/foo
"""

if not utool:
    utool = context.portal_url
base_url = context.getBaseUrl(utool=utool)

if not obj:
    obj = context

if hasattr(obj.aq_explicit, 'getRID'):
    # obj is a brain
    obj = obj.getObject()

context_url = base_url + utool.getRelativeUrl(obj)
if concat and context_url[-1] == '/':
    context_url = context_url[:-1]

return context_url
