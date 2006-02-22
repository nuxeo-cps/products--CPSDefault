===============
AjaxFolder View
===============
:Version: $Id$
:Author: Tarek Ziadé

Ajax folder view is a helper to move elements in an ordered folder.
It uses `getObjectPosition` and `moveObjectToPosition` apis
from `IOrderedContainer` interface.

Let's create a fake folder for our tests and plug the view::

    >>> class FakeFactory:
    ...     id = 'Link'
    ...
    >>> class FakePortalUrl:
    ...     def getPortalPath(self): return '/'
    ...
    >>> class FakeFolder:
    ...     items = []
    ...     portal_url = FakePortalUrl()
    ...     def __init__(self, id=''):
    ...         self.id = id
    ...
    ...     def getObjectPosition(self, id):
    ...         for item in self.items:
    ...             if isinstance(item, str) and item == id:
    ...                 return self.items.index(item)
    ...             elif hasattr(item, 'id') and item.id == id:
    ...                 return self.items.index(item)
    ...         return -1
    ...
    ...     def moveObjectToPosition(self, id, newpos):
    ...         oldpos = self.getObjectPosition(id)
    ...         temp = self.items[oldpos]
    ...         del self.items[oldpos]
    ...         self.items.insert(newpos, temp)
    ...
    ...     def objectIds(self):
    ...         ids = []
    ...         for element in self.items:
    ...             if isinstance(element, str):
    ...                 ids.append(element)
    ...             else:
    ...                 ids.append(element.id)
    ...         return ids
    ...
    ...     def restrictedTraverse(self, url, **kw):
    ...         if url.endswith(self.id):
    ...             return self
    ...         return FakeFolder()
    ...
    ...     def manage_CPScutObjects(self, ids):
    ...         for id in ids:
    ...             position = self.getObjectPosition(id)
    ...             if position != -1:
    ...                 del self.items[position]
    ...
    ...     def manage_CPSpasteObjects(self, cb):
    ...         pass
    ...
    ...     def __getitem__(self, id):
    ...         for element in self.items:
    ...             if isinstance(element, str) and id == element:
    ...                 return element
    ...             elif hasattr(element, 'id') and id == element.id:
    ...                 return element
    ...         raise AttributeError(id)
    ...
    ...     def allowedContentTypes(self):
    ...         return (FakeFactory(),)
    >>> MyFolder = FakeFolder('a')

Now let's try to move elements, dropping `a` on `c` moves `a` after `c`::

    >>> from Products.CPSDefault.browser.ajaxfolderview import AjaxFolderView
    >>> MyView = AjaxFolderView(MyFolder, None)
    >>> MyFolder.items = ['a', 'b', 'c']
    >>> MyView.moveElement('draggablea', 'droppablec')
    'b:c:a'
    >>> MyFolder.items
    ['b', 'c', 'a']

The dragged element is always placed **after** the dropped element,
dropping `c` on `a` moves `c` after `a`::

    >>> MyView = AjaxFolderView(MyFolder, None)
    >>> MyFolder.items = ['a', 'b', 'c']
    >>> MyView.moveElement('draggablec', 'droppablea')
    'a:c:b'
    >>> MyFolder.items
    ['a', 'c', 'b']

AjaxFolderView also know how to move an element in another container::

    >>> class FakeElement:
    ...     def __init__(self, id):
    ...         self.id = id
    ...         self.portal_type = 'Link'
    ...     def getContent(self):
    ...         return self
    ...     def absolute_url(self):
    ...         return 'url_%s_url' % self.id
    ...
    >>> MyView = AjaxFolderView(MyFolder, None)
    >>> MyFolder.items = [FakeElement('a'), FakeElement('b'), FakeElement('c')]
    >>> MyView.moveElement('draggablea', 'url:better.here')
    'b:c'
    >>> [item.id for item in MyFolder.items]
    ['b', 'c']

We aslo provide various guards to avoid silly drags::

    >>> MyView = AjaxFolderView(MyFolder, None)
    >>> MyFolder.items = [FakeElement('a'), FakeElement('b')]
    >>> MyView._checkElementMove('a', 'anywhere')
    True
    >>> MyView._checkElementMove('a', 'a')
    False
