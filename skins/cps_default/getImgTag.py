## Script (Python) "getImgTag"
##parameters=img_name, title=None, base_url=None, zoom=1, height=0, width=0
# $Id$
""" return an html img tag """

if not img_name:
    return ''
if base_url is None:
    base_url = context.getBaseUrl()
elif base_url == '':
    # img_name is a full path
    img_url = img_name

img_url = base_url + img_name
try:
    img = context.restrictedTraverse(img_name)
except KeyError:
    return '<img src="' + img_url + '">'
if not height:
    height = int(zoom * getattr(img, 'height', 0))
if not width:
    width = int(zoom * getattr(img,'width', 0))
tag = '<img src="%s" width="%s" height="%s" border="0" ' % (
    img_url, width, height )
if not title:
    title = img.title
if title:
    tag += 'title="' + title + '" '
return tag + '>'
