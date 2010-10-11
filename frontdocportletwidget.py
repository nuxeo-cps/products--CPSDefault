# (C) Copyright 2008 Association Paris-Montagne
# Author: Georges Racinet <georges.racinet@paris-montagne.org>
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
# $Id: __init__.py 890 2008-06-18 18:26:32Z joe $

import logging

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CPSSchemas.Widget import widgetRegistry
from Products.CPSSchemas.Widget import CPSWidget
from Products.CPSPortlets.CPSPortletWidget import CPSPortletWidget

from Products.CPSCore.interfaces import ICPSProxy
from Products.CPSDocument.interfaces import ICPSDocument

logger = logging.getLogger('Products.CPSDefault.frontdocportletwidget')

class CPSFrontDocumentPortletWidget(CPSPortletWidget):
    """Widget dedicated to rendering of front page documents.
    """

    meta_type = "Front Document Portlet Widget"

    _properties = CPSWidget._properties

    def prepare(self, ds, **kw):
        pass

    def validate(self, ds, **kw):
        return True

    def render(self, mode, ds, **kw):
        """Render the front page if any.

        Normally, context obj should be a folder with the folder_display_options
        schema
        """
        if mode != 'view':
            raise RuntimeError(
                "Widget %s should be rendered in 'view' mode only" % self)

        utool = getToolByName(self, 'portal_url')

        # retrieving cautiously folder options
        folder_proxy = kw.get('context_obj')
        if folder_proxy is None:
            logger.warn("Called with no context_obj")
            return ''
        if not ICPSProxy.providedBy(folder_proxy):
            logger.debug("not a proxy: %s", utool.getRpath(folder_proxy))
            return ''
        folder_doc = folder_proxy.getContent()
        if not ICPSDocument.providedBy(folder_doc):
            logger.debug("proxy content not a CPSDocument: %s",
                         utool.getRpath(folder_proxy))
            return ''
        folder_dm = folder_doc.getDataModel(proxy=folder_proxy)
        frontpage_id = folder_dm.get('frontpage')
        if not frontpage_id:
            return ''

        # retrieving front page
        try:
            front_proxy = folder_proxy[frontpage_id]
        except (KeyError, AttributeError):
            logger.warn("Folder at %s has front page document '%s' "
                        "that does not exist",
                        utool.getRpath(folder_proxy), frontpage_id)
            return ''

        # final rendering according to settings from datastructure
        front_doc = front_proxy.getContent()
        cluster = str(ds.get('cluster_id'))
        excluded = ds.get('excluded_layouts', ())

        stylesheet = '<link rel="Stylesheet" type="text/css" href="%s%s"/>' % (
            utool.getBaseUrl(), 'document.css')

        rendered = front_doc.render(cluster=cluster, excluded_layouts=excluded,
                                    proxy=front_proxy,
                                    context=front_proxy,)
        css = ds.get('css_class')
        if css:
            rendered = '<div class="%s">%s</div>' % (css, rendered)

        # TODO This isn't valid XHTML but does the trick for now.
        # Once #1976 is ready, cleanly require stylesheet for <head> inclusion.
        return stylesheet + rendered

widgetRegistry.register(CPSFrontDocumentPortletWidget)
