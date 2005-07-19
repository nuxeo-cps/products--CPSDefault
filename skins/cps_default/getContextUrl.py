##parameters=obj=None, utool=None, concat=0
# $Id$
"""
Return the minimal url to access the object ex: /, /cps/foo

If concat=1 there is no trailing '/' ex: '', /cps/foo

XXX AT: this is just an helper script, absolute_url_path gives all we'd like to
have and deals with virtual hosting. This script is only here for compatibility
reasons.
"""

if obj is None:
    obj = context

if hasattr(obj.aq_explicit, 'getRID'):
    # obj is a brain
    obj = obj.getObject()

context_url = obj.absolute_url_path()
if not concat:
    context_url = context_url + '/'

return context_url
