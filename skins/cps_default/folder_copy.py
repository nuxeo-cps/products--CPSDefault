##parameters=ids=[], REQUEST=None
#$Id$
"""
Copy objects from the clipboard.

Used within the folder_contents template.
"""

if ids:
    context.manage_CPScopyObjects(ids, REQUEST)
    message = 'psm_item(s)_copied'
else:
    message = 'psm_select_at_least_one_document'

if REQUEST is not None:
    ret_url = context.absolute_url() + '/folder_contents'
    return REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' %
                                        (ret_url, message))
