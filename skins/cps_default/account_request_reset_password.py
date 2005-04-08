##parameters=username_or_email, REQUEST
# $Id$
"""
Send a password request to the membership tool and display a message telling if
everything went fine or not.
"""

from Products.CMFCore.utils import getToolByName

membership_tool = getToolByName(context, 'portal_membership')

try:
    membership_tool.requestPasswordReset(username_or_email)
    REQUEST.RESPONSE.redirect("%s/?portal_status_message=%s" %
                              (context.absolute_url(),
                               'psm_reset_password_request_received'))
except ValueError:
    REQUEST.RESPONSE.redirect("%s/account_lost_password_form?portal_status_message=%s" %
        (context.absolute_url(), 'psm_join_invalid_name'))
