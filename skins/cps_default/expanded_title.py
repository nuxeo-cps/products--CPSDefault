## Script (Python) "expanded_title"
##parameters=
##title=Build title which includes site title
##
# $Id$
#
# Fix for #1895: UnicodeDecodeError when viewing a calendar if CPS site title
# has accented characters.
# BBB: Remove this customized script when the switch to UTF8 is done.

from Products.CPSUtil.text import toLatin9

site_title = context.portal_url.getPortalObject().Title()
page_title = context.Title()
page_title = toLatin9(page_title)

if page_title != site_title:
   page_title = site_title + ": " + page_title

return page_title

