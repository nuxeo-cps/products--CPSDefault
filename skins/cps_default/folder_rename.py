##parameters=
# $Id$

"""
Rename objects which ids are passed in the request. Used within the
folder_contents template.
"""

REQUEST = context.REQUEST

new_ids = [context.computeId(id) for id in REQUEST['new_ids']]

context.manage_renameObjects(REQUEST['ids'], new_ids, REQUEST) 

return REQUEST.RESPONSE.redirect(context.absolute_url() + \
                                ('/folder_contents?portal_status_message=%s' \
                                % ('psm_item(s)_renamed',)))
