##parameters=username, d, t, REQUEST

from Products.CMFCore.utils import getToolByName

request_emission_time = d
reset_token = t

membership_tool = getToolByName(context, 'portal_membership')
result = membership_tool.resetPassword(username,
                                       request_emission_time, reset_token)

if result['reset_password_success'] and result['email_password_success']:
    REQUEST.RESPONSE.redirect("%s/login_form?portal_status_message=%s" %
                              (context.absolute_url(),
                               "psm_reset_password_success"))
else:
    REQUEST.RESPONSE.redirect("%saccount_lost_password_form/?portal_status_message=%s" %
                              (context.absolute_url(),
                               "psm_reset_password_problem"))
