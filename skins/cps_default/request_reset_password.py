##parameters=username, REQUEST

from Products.CMFCore.utils import getToolByName

# context.portal_membership
membership_tool = getToolByName(context, 'portal_membership')
reset_token = membership_tool.requestPasswordReset(username)

# XXX: Send email
# sendEmail(username, reset_token)
REQUEST.RESPONSE.redirect("%s/?portal_status_message=%s" %
                          (context.absolute_url(),
                           "psm_reset_request_received with token = %s" % reset_token))


