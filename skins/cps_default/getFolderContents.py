## Script (Python) "getFolderContents"
##parameters=contentFilter=None
##title=
##
"""
Get a datastructure describing what's in a folder.
"""
bmt = context.Benchmarktimer('getFolderContent')
bmt.start()

mtool=context.portal_membership
wtool=context.portal_workflow
fc = []
for item in context.objectValues():
    if item.getId().startswith('.'):
        continue
    if not mtool.checkPermission('View', item):
        continue
    fc.append(item)

def title_cmp(a, b): # cmp by folder then title
    return (-cmp(a.isPrincipiaFolderish, b.isPrincipiaFolderish) or
            cmp(a.title_or_id().lower(), b.title_or_id().lower()) or
            0
            )

def status_cmp(a, b):
    return (-cmp(a.isPrincipiaFolderish, b.isPrincipiaFolderish) or
            cmp(wtool.getInfoFor(a, 'review_state', ''),
                wtool.getInfoFor(b, 'review_state', '')) or
            cmp(a.title_or_id().lower(), b.title_or_id().lower()) or
            0
            )

fc.sort(title_cmp)

bmt.stop()
bmt.saveProfile(context.REQUEST)

return fc
