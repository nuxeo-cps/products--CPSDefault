##parameters=who, REQUEST
# $Id$
"""
Send a password request to the membership tool and display a message telling if
everything went fine or not.
"""

from Products.CMFCore.utils import getToolByName

mtool = getToolByName(context, 'portal_membership')
portal = getToolByName(context, 'portal_url').getPortalObject()

mtool.requestPasswordReset(who)

# We don't care about whether it works or not, we don't want
# to give info to a potential attacker. So no result is checked.

REQUEST.RESPONSE.redirect("%s?who=%s" %
                          (portal.account_request_reset_password_info.absolute_url(),
                           who))

