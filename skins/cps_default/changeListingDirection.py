## Script (Python) "changeListingDirection"
##parameters=
# $Id$
""" Change the direction of the item display within a folder """

portal_url  = context.portal_url()
context_url = context.REQUEST.get("context_url", context.getContextUrl())

# cps cookie checking
cps_cookie = context.REQUEST.SESSION.get('cps_preferences', {})
display_direction = cps_cookie.get('cps_display_direction', "asc")

if display_direction == "asc":
    display_direction = "desc"
else:
    display_direction = "asc"
    
cookieName  = 'cps_display_direction'
cookieValue = display_direction
cps_cookie[cookieName] = cookieValue
context.REQUEST.SESSION['cps_preferences'] = cps_cookie

display_change  = context.REQUEST.form.get('change_display', 0)
redirection_url = context_url + "/folder_contents?change_display=%s" %display_change
    
context.REQUEST.RESPONSE.redirect(redirection_url)
    



