## Script (Python) "FilterContents"
##parameters=items=[], sort_by='title', direction=None, hide_folder=0
# $Id$
"""
Filter and sort items (proxy)
"""
mtool=context.portal_membership
wtool=context.portal_workflow

# filtering
filtered_items = []
now = context.ZopeTime()
for item in items:
    if item.getId().startswith('.'):
        continue
    if not mtool.checkPermission('View', item):
        continue
    if hide_folder and item.isPrincipiaFolderish:
        continue

# XXX TODO expire should be handel by wf
    filtered_items.append(item)

# sorting
# XXX hardcoded status !
status_sort_order={'nostate':'0',
                   'pending':'1',
                   'published':'2',
                   'work':'3',
                   }

def id_sortkey(a):
    return str(not a.isPrincipiaFolderish) + \
           a.getId()

def status_sortkey(a):
    return str(not a.isPrincipiaFolderish) + \
           status_sort_order[wtool.getInfoFor(a,'review_state','nostate')] + \
           a.title_or_id().lower()

def title_sortkey(a):
    return str(not a.isPrincipiaFolderish) + \
           a.title_or_id().lower()

def date_sortkey(a):
    return str(not a.isPrincipiaFolderish) + \
           str(wtool.getInfoFor(a,'time','x')) + \
           a.getId()

def cmp_desc(x, y):
    return -cmp(x, y)

make_sortkey = id_sortkey
if sort_by == 'status':
    make_sortkey = status_sortkey
elif sort_by == 'date':
    make_sortkey = date_sortkey
elif sort_by == 'title':
    make_sortkey = title_sortkey

objects = [ ( make_sortkey(x), x ) for x in filtered_items ]

if direction == 'desc':
    objects.sort(cmp_desc)
elif direction == 'asc':
    objects.sort() # tuples compare "lexicographically"
else:
    pass

filtered_items = [ x[1] for x in objects ]

return filtered_items
