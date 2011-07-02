# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
# G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.CPSCore.utils import bhasattr
from roots import RootXMLAdapter

from OFS.interfaces import IOrderedContainer
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.CPSCore.interfaces import ICPSProxy

class ProxyXMLAdapter(RootXMLAdapter, PropertyManagerHelpers):
    """Export/import adapter for CPS Proxies.

    Warning: in theory proxies could point to anything, but this adapter
    assumes that every proxy is a Proxy Document or Folder, namely that
    it has a portal_type and its creation is managed by the workflow tool.
    This is not the only place in CPS where such assumptions are being made.

    This inherits RootXMLAdapter to add import/export of the sub-proxy
    declarations, to avoid code duplication right now, but could become
    the main adapter.
    """

    name = 'proxies'

    adapts(ICPSProxy, ISetupEnviron)

    implements(IBody)

    def __init__(self, context, environ):
        super(self.__class__, self).__init__(context, environ)
        self.wftool = getToolByName(context, 'portal_workflow')

    def _importNode(self, node):
        super(self.__class__, self)._importNode(node)
        self._initProperties(node)
        self._initProxies(node)
        self._initObjects(node)

    def _exportNode(self):
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractProxies())
        node.appendChild(self._extractObjects())
        return node

    node = property(_exportNode, _importNode)

    def _initProxies(self, node):
        container = self.context
        for child in node.childNodes:
            if child.nodeName != 'proxy':
                continue
            pid = child.getAttribute('name')
            if not container.hasObject(pid):
                self._createProxy(child, pid)
            elif child.hasAttribute('remove'):
                container._delObject(pid)
                continue

            obj = getattr(self.context, pid)
            importer = queryMultiAdapter((pid, self.environ), INode)
            if importer:
                importer.node = child

            # TODO: support insert-before, insert-after

    def _createProxy(self, node, pid):
        portal_type = str(node.getAttribute('portal_type'))
        if not portal_type:
            raise ValueError("Proxy %r must be created in %s, "
                             "but portal_type is not specified.", pid,
                             self.context)
        # GR conversion to str are necessary, otherwise it'll be unicode
        self.wftool.invokeFactoryFor(self.context, str(portal_type), str(pid))

    def _extractProxies(self):
        fragment = self._doc.createDocumentFragment()
        for proxy in self.context.objectValues('CPS Proxy Folder'):
            node = self._doc.createElement('proxy')
            node.setAttribute('portal_type', proxy.portal_type)
            node.setAttribute('name', proxy.getId())
            fragment.appendChild(node)
        return fragment

    def _extractObjects(self):
        """Identical to ObjectManagerHelpers, but skips proxies."""
        fragment = self._doc.createDocumentFragment()
        # GR: this can become problematic for large BTrees, but the sorting
        # has its benefits in terms of diff between subsequent exports
        if bhasattr(self.context, 'iterValues'):
            values = self.context.iterValues
        else:
            values = self.context.objectValues

        objects = [obj for obj in values()
                   if not ICPSProxy.providedBy(obj)]

        if not IOrderedContainer.providedBy(self.context):
            objects = list(objects)
            objects.sort(lambda x,y: cmp(x.getId(), y.getId()))
        for obj in objects:
            exporter = queryMultiAdapter((obj, self.environ), INode)
            if exporter:
                node = exporter.node
                if node is not None:
                    fragment.appendChild(exporter.node)
        return fragment
