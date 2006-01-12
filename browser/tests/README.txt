===============
AjaxFolder View
===============
:Version: $Id$
:Author: Tarek Ziadé

Ajax folder view is a helper to move elements in an ordered folder.
It uses `getObjectPosition` and `moveObjectToPosition` apis
from `IOrderedContainer` interface.

Let's create a fake folder for our tests and plug the view::

    >>> class FakeFolder:
    ...     items = []
    ...
    ...     def getObjectPosition(self, id):
    ...         return self.items.index(id)
    ...
    ...     def moveObjectToPosition(self, id, newpos):
    ...         oldpos = self.getObjectPosition(id)
    ...         temp = self.items[oldpos]
    ...         self.items[oldpos] = self.items[newpos]
    ...         self.items[newpos] = temp
    ...
    ...     def objectIds(self):
    ...         return self.items
    >>> MyFolder = FakeFolder()

Now let's try to move elements::

    >>> from Products.CPSDefault.browser.ajaxfolderview import AjaxFolderView
    >>> MyView = AjaxFolderView(MyFolder, None)
    >>> MyFolder.items = ['a', 'b', 'c']
    >>> MyView.moveElement('draggablea', 'droppablec')
    'c:b:a'
    >>> MyFolder.items
    ['c', 'b', 'a']


