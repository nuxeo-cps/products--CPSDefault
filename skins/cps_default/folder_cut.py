##parameters=ids={}, REQUEST=None
#$Id$

"""
Cut an object. Used within the folder_contents template.
"""

if ids:
    context.manage_CPScutObjects(ids, REQUEST)
    message = 'psm_item(s)_cut'
else:
    message = 'psm_select_at_least_one_document'

ret_url = context.absolute_url() + '/folder_contents'
return REQUEST.RESPONSE.redirect(
    ret_url + '?portal_status_message=%s' % message)
