## Script (Python) "getFolderContents"
##parameters=contentFilter=None
##title=
##
"""
Get a datastructure describing what's in a folder.
"""

mtool=context.portal_membership;
fc = []
for item in context.listFolderContents(contentFilter=contentFilter):
    if item.getId().startswith('.'):
        continue
    if not mtool.checkPermission('View', item):
        continue
    fc.append(item)

def thecmp(a, b): # cmp by folder then title
    return (-cmp(a.isPrincipiaFolderish, b.isPrincipiaFolderish) or
            cmp(a.title_or_id().lower(), b.title_or_id().lower()) or
            0
            )

fc.sort(thecmp)

return fc
