##parameters=img_name, title=None, base_url=None, zoom=1, height=0, width=0, alt='', keep_ratio=0
# $Id$
"""
Return an HTML img tag

FIXME: need more explanation. What are the parameters?
"""

if not img_name:
    return ''
if base_url is None:
    base_url = context.getBaseUrl()
elif base_url == '':
    pass # image name is a full path
img_url = base_url + img_name
try:
    img = context.restrictedTraverse(img_name)
except (KeyError, 'NotFound'):
    return '<img src="%s" alt="%s" />' % (img_url, alt)

# XXX: workaround BMP bug
# Note: int(getattr(img, 'height', 0)) raises :
# ValueError: invalid literal for int()
original_height = getattr(img, 'height', 0)
original_width = getattr(img, 'width', 0)

if not height:
    height = int(zoom * original_height)
if not width:
    width = int(zoom * original_width)

if keep_ratio:
    z_w = z_h = 1
    h = original_height
    w = original_width
    if w and h:
        if w > int(width):
            z_w = int(width) / float(w)
        if h > int(height):
            z_h = int(height) / float(h)
        zoom = min(z_w, z_h)
        width = int(zoom * w)
        height = int(zoom * h)

if width and height:
    tag = '<img src="%s" width="%s" height="%s" alt="%s"' % (
        img_url, str(width), str(height), alt)
else:
    tag = '<img src="%s" alt="%s"' % (img_url, alt)
if not title:
    title = getattr(img, 'title', None)
if title:
    tag += ' title="' + title + '"'
return tag + ' />'
