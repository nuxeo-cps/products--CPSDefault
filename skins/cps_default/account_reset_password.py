##parameters=u, w, d, t, REQUEST
# $Id$
"""
u: usernames
w: who
d: time
t: token

Make the membership tool reset the password for the given usernames and display
their new (identic) password as a portal status message or a message telling
that something went wrong.

Usually this script is called with only one username but resetPassword works for
many users as well.
"""

from Products.CMFCore.utils import getToolByName

membership_tool = getToolByName(context, 'portal_membership')
if u:
    password = membership_tool.resetPassword(u, w, d, t)
else:
    password = None

if password is not None:
    # Here we don't want to do a redirect since we want to display the new
    # password and we don't want the new password to appear in the URL.
    REQUEST.form.update({
     'portal_status_message': 'psm_reset_password_success_and_new_password_is',
     'portal_status_message_mappings': {
        'new_password': password,
        },
     'username': u[0],
     })
    return context.login_form()
else:
    REQUEST.RESPONSE.redirect('%s/account_lost_password_form/'
                              '?portal_status_message=%s' %
                              (context.absolute_url(),
                               'psm_reset_password_problem'))
