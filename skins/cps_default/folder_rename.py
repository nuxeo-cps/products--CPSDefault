## Script (Python) "folder_rename"
##title=Rename Object
##parameters=
# $Id$

"""
Rename objects which ids are passed in the request. Used within the
folder_contents template.
"""

REQUEST = context.REQUEST

context.manage_renameObjects(REQUEST['ids'], REQUEST['new_ids'], REQUEST)

return REQUEST.RESPONSE.redirect(context.absolute_url() + \
                                ('/folder_contents?portal_status_message=%s' \
                                % ('psm_item(s)_renamed',)))
