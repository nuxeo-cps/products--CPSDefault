## Script (Python) "getImgTag"
##parameters=img_name, title=None, base_url=None
# $Id$
""" return an html img tag """
if not img_name:
    return ''
if not base_url:
    base_url = context.getBaseUrl()
img_url = base_url + img_name
try:
    img = context.restrictedTraverse(img_name)
except KeyError:
    return '<img src="' + img_url + '">'

tag = '<img src="%s" width="%s" height="%s" border="0" ' % (
    img_url, img.width, img.height)
if not title:
    title = img.title
if title:
    tag += 'title="' + title + '" '
return tag + '>'
