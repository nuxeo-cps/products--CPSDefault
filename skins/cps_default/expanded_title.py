## Script (Python) "expanded_title"
##parameters=
##title=Build title which includes site title, page title and site description
##
# $Id$
#
# Fix for #1895: UnicodeDecodeError when viewing a calendar if CPS site title
# has accented characters.
#
# TODO: Depending on what CMF does, maybe remove this customized script when the
# switch to UTF8 is done.

site_title = context.portal_url.getPortalObject().Title()
site_description = context.portal_url.getPortalObject().Description()
page_title = context.Title()

if page_title == site_title:
    # This is portal root (homepage) or a page not corresponding to a document
    expanded_title = site_title + ': ' + site_description
else:
    # Here it's more meaningful to put the title after the title
    # of the page especially when the whole title is long
    # and the page is bookmarked.
    expanded_title = page_title + ' | ' + site_title

return expanded_title

