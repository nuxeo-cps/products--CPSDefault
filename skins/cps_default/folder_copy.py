##parameters=
#$Id$

"""
Copy an object. Used within the folder_contents template.
"""

REQUEST=context.REQUEST

if REQUEST.has_key('ids'):
    context.manage_CPScopyObjects(REQUEST['ids'], REQUEST)
    message = 'psm_item(s)_copied'
else:
    message = 'psm_select_at_least_one_document'

return REQUEST.RESPONSE.redirect(context.absolute_url() + \
                                 ('/folder_contents?portal_status_message=%s' \
                                  % (message, )))
