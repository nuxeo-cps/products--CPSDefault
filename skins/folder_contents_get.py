##parameters=contentFilter=None
"""
Get a datastructure describing what's in a folder.
"""

mtool=context.portal_membership;
docinfos = []
for item in context.listFolderContents(contentFilter=contentFilter):
    if item.getId().startswith('.'):
        continue
    if not mtool.checkPermission('View', item):
        continue
    docinfos.append(item)


return docinfos
