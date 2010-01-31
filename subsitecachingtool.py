# -*- coding: iso-8859-15 -*-
# (C) Copyright 2005 Viral Productions <http://viral-prod.com>
# Author: Georges Racinet <georges.racinet@viral-prod.com>
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
# $Id: ViralProdTool.py 1077 2009-11-27 01:06:05Z joe $

"""A tool to handle caching headers for a whole hierarchy.

This is different from CachingHeaderPolicy, because this is based mostly
on the place in the folder hierarchy, which is not convenient to handle with
the latter.

"""

from DateTime.DateTime import DateTime
from Acquisition import aq_inner, aq_parent
from Globals import InitializeClass

from Products.CMFCore.utils import SimpleItemWithProperties, UniqueObject
from Products.CMFCore.utils import getToolByName

from Products.CPSCore.interfaces import ICPSSite
from Products.CPSPortlets.CPSPortlet import CPSPortlet

from voidresponses import SUBSITE_LAST_MODIFIED_DATE

class SubSiteCachingTool(UniqueObject, SimpleItemWithProperties):

    id = 'portal_subsite_caching'

    _properties = (
        dict(id='default_cache_control', type='string', mode='w',
             label='Default value of Cache Control header'),
        )

    default_cache_control = 'max-age:36000; must-revalidate'

    def setCacheControlHeader(self, response):
        response.setHeader('Cache-Control', self.default_cache_control)

    def notify_event(self, event_type, obj, infos):
        """Catch publication events for the caching headers."""

        if event_type in ['workflow_publish', 'workflow_accept',
                          'sys_modify_security'] \
           or isinstance(object, CPSPortlet):
            self.updateLastModified(obj)

    def updateLastModified(self, obj):
        while obj is not None:
            # acquire last modified date
            lmd = getattr(obj, SUBSITE_LAST_MODIFIED_DATE, None)
            if lmd is None:
                return
            lmd.set(DateTime())

            # start again from above the one we've found
            container = aq_parent(aq_inner(lmd))
            if ICPSSite.providedBy(container):
                obj = None
            obj = aq_parent(aq_inner(container))


InitializeClass(SubSiteCachingTool)
