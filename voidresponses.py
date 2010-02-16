# (C) Copyright 2009 Georges Racinet, Nuxeo SA
# Author: Georges Racinet <georges@racinet.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: interfaces.py 53724 2009-07-04 12:29:21Z gracinet $

import logging

from DateTime.DateTime import DateTime

from Products.CMFCore.utils import getToolByName

SUBSITE_LAST_MODIFIED_DATE = '.cps_subsite_last_modified_date'

logger = logging.getLogger('Products.CPSDefault.voidresponses')

class DummyVoidResponseHandler:
    """Just there to avoid a miss in component lookup
    """

    def __init__(self, context, request):
        pass

    def respond(self, portal=None):
        pass

class BaseResponseHandler:
    def __init__(self, context, request):
        self.context = context
        self.request = request

class ImsResponseHandler(BaseResponseHandler):

    def isHttpCacheable(self):
        return getToolByName(self.context, 'portal_membership').isAnonymousUser()

    def setCachingHeaders(self, lmd):
        """Put appropriate headers for HTTP caching."""

        resp = self.request.RESPONSE
        if self.isHttpCacheable():
            sct = getToolByName(self.context, 'portal_subsite_caching', None)
            if sct is None:
                resp.setHeader('Cache-Control',
                               'max-age:36000; must-revalidate')
            else:
                sct.setCacheControlHeader(resp)
            resp.setHeader('Last-Modified', lmd.rfc822())

    def imsRespond(self, portal=None):
        """Respond to If-Modified-Since request. Return True in case of 304"""

        # acquire last_modified
        lmd = getattr(self.context, SUBSITE_LAST_MODIFIED_DATE, None)
        if lmd is None:
            return False

        lmd = lmd.value # can be None
        request = self.request
        header = request.get_header('If-Modified-Since', None)
        if not self.isHttpCacheable():
            return False

        if header is None:
            # non conditional request, still needs the correct Last-Modified
            self.setCachingHeaders(lmd)
            return False

        #
        # header parsing taken from OFS.Image.File
        #
        header=header.split( ';')[0]
        # Some proxies seem to send invalid date strings for this
        # header. If the date string is not valid, we ignore it
        # rather than raise an error to be generally consistent
        # with common servers such as Apache (which can usually
        # understand the screwy date string as a lucky side effect
        # of the way they parse it).
        # This happens to be what RFC2616 tells us to do in the face of an
        # invalid date.
        try:
            ims = DateTime(header)
        except:
            logger.warn("Couldn't parse If-Modified-Since header: %s",
                        header)
            ims = None

        if lmd > ims:
            self.setCachingHeaders(lmd)
            return False
        else:
            request.RESPONSE.setStatus(304)
            return True

    def respond(self, portal=None):
        return self.imsRespond()
