## Script (Python) "getFolderContents"
##parameters=sort_by='title', direction='asc'
##title=
##
"""
Get a sorted list of contents object
"""
bmt = context.Benchmarktimer('getFolderContent', level=-2)
bmt.start()

mtool=context.portal_membership
wtool=context.portal_workflow

# filtering
items = []
now = context.ZopeTime()
for item in context.objectValues():
    if item.getId().startswith('.'):
        continue
    if not mtool.checkPermission('View', item):
        continue
    if item.effective() <= now and item.expires() > now:
        items.append(item)

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
           str(wtool.getInfoFor(a,'time','x').timeTime()) + \
           a.getId()

def cmp_desc(x, y):
    return -cmp(x, y)

make_sortkey = id_sortkey
if sort_by == 'status':
    make_sortkey = status_sortkey
elif sort_by == 'date':
    make_sortkey = status_sortkey
elif sort_by == 'title':
    make_sortkey = title_sortkey
    
objects = [ ( make_sortkey(x), x ) for x in items ]
if direction != 'asc':
    objects.sort(cmp_desc)
else:
    objects.sort() # tuples compare "lexicographically"
items = [ x[1] for x in objects ]

bmt.stop()
bmt.saveProfile(context.REQUEST)

return items
