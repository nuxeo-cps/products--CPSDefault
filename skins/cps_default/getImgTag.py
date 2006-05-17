##parameters=img_name, title=None, base_url=None, zoom=1, height=None, width=None, alt='', keep_ratio=0, img=None
# $Id$
"""
Return an HTML img tag

   img is the image object. If missing, traversal based on img_name is attempted
   img_name is a path to build the image URL.
   base_url is used to build the image full URL.
         if missing, the portal base_url is used instead.
         use '' to indicate that img_name is an absolute path (starts with '/')
"""

import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('getImgTag')

if not img_name:
    return ''

# URL for the src attribute
if not base_url:
    utool = getToolByName(context, 'portal_url')
    if base_url != '': # img_name is not an absolute path
        base_url = utool.getBaseUrl()
img_url = base_url + img_name

# retrieving the image object is necessary for resizing
# we use img_name to guess the path
if img is None:
   if img_name[0] == '/':
       # leading '/' would refer to app object, not what we want
       trav_base = utool.getPortalObject()
       trav_path = img_name[1:]
   else:
       trav_base = context
       trav_path = img_name
   logger.debug('traversal to img object: %s (from %s)...' % (trav_path,
                                                              trav_base))
   try:
        img = trav_base.restrictedTraverse(trav_path, default=None)
   except (KeyError, AttributeError, 'NotFound'):
        logger.debug('...not found')

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
