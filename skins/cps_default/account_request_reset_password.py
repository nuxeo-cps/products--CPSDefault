##parameters=username, REQUEST

from Products.CMFCore.utils import getToolByName

membership_tool = getToolByName(context, 'portal_membership')
membership_tool.requestPasswordReset(username)

REQUEST.RESPONSE.redirect("%s/?portal_status_message=%s" %
                          (context.absolute_url(),
                           "psm_reset_password_request_received"))
