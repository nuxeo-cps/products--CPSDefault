## Script (Python) "removeDisplayParams"
##parameters=
# $Id$
""" Remove the user display params within the SESSION """

context_url = context.REQUEST.get("context_url", context.getContextUrl())

if context.REQUEST.SESSION.has_key('cps_display_params'):
    del context.REQUEST.SESSION['cps_display_params']

redirection_url = context_url + "/folder_contents"
context.REQUEST.RESPONSE.redirect(redirection_url)
