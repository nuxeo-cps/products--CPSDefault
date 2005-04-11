##parameters=usernames, email, d, t, REQUEST
# $Id$
"""
Make the membership tool reset the password for the given usernames and display
their new (identic) password as a portal status message or a message telling
that something went wrong.

Usually this script is called with only one username but resetPassword works for
many users as well.
"""

from Products.CMFCore.utils import getToolByName

request_emission_time = d
reset_token = t

membership_tool = getToolByName(context, 'portal_membership')
result = membership_tool.resetPassword(usernames, email,
                                       request_emission_time, reset_token)

if result['reset_password_success']:
    # Here we don't want to do a redirect since we want to display the new
    # password and we don't want the new password to appear in the URL.
    REQUEST.form['portal_status_message'] = 'psm_reset_password_success_and_new_password_is'
    REQUEST.form['portal_status_message_mappings'] = {'new_password': result['new_password']}
    REQUEST.form['username'] = usernames[0]
    return context.login_form()
else:
    REQUEST.RESPONSE.redirect("%saccount_lost_password_form/?portal_status_message=%s" %
                              (context.absolute_url(),
                               "psm_reset_password_problem"))
