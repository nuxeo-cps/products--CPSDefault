##parameters=img_name, title=None, base_url=None, zoom=1, height=None, width=None, alt='', keep_ratio=0
# $Id$
"""
Return an HTML img tag

FIXME: need more explanation. What are the parameters?
"""

from zLOG import LOG, DEBUG

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
    img = None

if img is None:
    tag = '<img src="%s" alt="%s" />' % (img_url, alt)
else:
    # Fix the BMP bug (#305): Zope is unable to detect height and width for BMP
    # images and thus this properties are valued to the empty string for BMP
    # files

    original_height = None
    try:
        original_height = int(img.getProperty('height', ''))
    except (AttributeError, ValueError):
        pass

    original_width = None
    try:
        original_width = int(img.getProperty('width', ''))
    except (AttributeError, ValueError):
        pass

    if height is None and original_height is not None:
        height = int(zoom * original_height)
    if width is None and original_width is not None:
        width = int(zoom * original_width)

    if (keep_ratio
        and original_height is not None
        and original_width is not None):
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

    if width is not None and height is not None:
        tag = '<img src="%s" width="%s" height="%s" alt="%s"' % (
            img_url, str(width), str(height), alt)
    else:
        tag = '<img src="%s" alt="%s"' % (img_url, alt)

    if not title:
        title = getattr(img, 'title', None)
    if title:
        tag += ' title="' + title + '"'

    tag += ' />'

return tag
