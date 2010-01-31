##parameters=obj=None, utool=None, concat=0
# $Id$
"""
DO NOT USE THIS DEPRECATED SCRIPT, USE absolute_url_path instead.
(obj.absolute_url_path() will give /cps/foo.)


Return the minimal url to access the object ex: /, /cps/foo/

If concat=1 there is no trailing '/' ex: '', /cps/foo
"""

if obj is None:
    obj = context

from AccessControl import Unauthorized

try:
    if hasattr(obj.aq_explicit, 'getRID'):
        # obj is a brain
        obj = obj.getObject()
except Unauthorized: # happens in error rendering context
    pass

context_url = obj.absolute_url_path()
if not concat:
    context_url = context_url + '/'

return context_url
