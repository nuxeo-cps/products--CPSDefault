##parameters=img_name, title=None, base_url=None, zoom=1, height=0, width=0, alt='', keep_ratio=0
# $Id$
""" return an html img tag"""
if not img_name:
    return ''
if base_url is None:
    base_url = context.getBaseUrl()
elif base_url == '':
    pass # image name is a full path
img_url = base_url + img_name
try:
    img = context.restrictedTraverse(img_name)
except KeyError:
    return '<img src="' + img_url + '" alt="">'

if not height:
    height = int(zoom * getattr(img, 'height', 0))
if not width:
    width = int(zoom * getattr(img,'width', 0))

if keep_ratio:
    z_w = z_h = 1
    h = int(getattr(img, 'height', 0))
    w = int(getattr(img, 'width', 0))
    if w and h:
        if w > int(width):
            z_w = int(width) / float(w)
        if h > int(height):
            z_h = int(height) / float(h)
        zoom = min(z_w, z_h)
        width = int(zoom * w)
        height = int(zoom * h)

if width or height:
    tag = '<img src="%s" width="%s" height="%s" border="0" alt="%s"' % (
        img_url, str(width), str(height), alt )
else:
    tag = '<img src="%s" border="0" alt="%s"' % ( img_url, alt )
if not title:
    title = getattr(img, 'title', None)
if title:
    tag += ' title="' + title + '"'
return tag + '>'
