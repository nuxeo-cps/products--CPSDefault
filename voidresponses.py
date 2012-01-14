# (C) Copyright 2009 Georges Racinet, Nuxeo SA
#               2012 CPS-CMS Community <http://cps-cms.org/>
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

import logging

from AccessControl import Unauthorized
from DateTime.DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CPSDefault.permissions import ModifyFolderProperties

from Products.CPSUtil.conflictresolvers import IncreasingDateTime
from Products.CPSUtil.http import is_modified_since

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
            if lmd is not None:
                resp.setHeader('Last-Modified', lmd.rfc822())

    def imsRespond(self, portal=None):
        """Respond to If-Modified-Since request. Return True in case of 304"""

        if not self.isHttpCacheable():
            return False

        lmd = self.getLastModificationDate(self.context)
        if lmd is None:
            return False

        if is_modified_since(self.request, lmd):
            self.setCachingHeaders(lmd)
            return False

        return True

    def respond(self, portal=None):
        return self.imsRespond()

    @classmethod
    def enableIfModifiedSince(cls, folder, lastmod=None):
        """Prepare folder for If-Modified-Since conditional requests.

        By calling this function, the user promises that the content presented
        below the given folder never has to take into accounts content from
        outside this folder. For instance, there should not be any Content
        Portlet listing documents outside this folder.

        In return, CPS will maintain a date/time of last modification for this
        whole subhierarchy, publish it in relevant HTTP headers, and handle
        time based conditional requests (If-Modified-Since) accordingly.
        See also trac #2050 and doc/howto-http-caching.txt

        The optional lastmod parameter allows to directly set the value of last
        modification date/time. It is mostly intended for unit tests.
        If missing, the current date/time will be used.
        """
        if not _checkPermission(ModifyFolderProperties, folder):
            raise Unauthorized("You are not authorized to enable this folder "
                               "for conditional requests.")

        if folder.hasObject(SUBSITE_LAST_MODIFIED_DATE):
            lmd = folder[SUBSITE_LAST_MODIFIED_DATE]
        else:
            lmd = IncreasingDateTime(SUBSITE_LAST_MODIFIED_DATE)
            folder._setObject(SUBSITE_LAST_MODIFIED_DATE, lmd)
        if lastmod is None:
            lastmod = DateTime()

        lmd.set(lastmod)

    @classmethod
    def getLastModificationDate(cls, obj):
        """Read the relevant last modification date for given object.

        As used in the handler : acquire it from an upper folder where it's
        been set.
        """
        lmd = getattr(obj, SUBSITE_LAST_MODIFIED_DATE, None)
        if lmd is None:
            return None
        return lmd.value # may also be None
