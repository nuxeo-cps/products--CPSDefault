##parameters=items=[], sort_by='title', direction=None, hide_folder=0, displayed=['']
# $Id$
"""
Filter and sort items (proxy)
"""
mtool = context.portal_membership
wtool = context.portal_workflow
ttool = context.portal_types

from zLOG import LOG, DEBUG

# filtering
filtered_items = []
now = context.ZopeTime()
display_cache = {}
for item in items:
    if item.getId().startswith('.'):
        continue
    if not mtool.checkPermission('View', item):
        continue

    # Using a cache to optimize the retrieval of the
    # 'cps_display_as_document_in_listing' attribute.
    portal_type = getattr(item, 'portal_type', None)
    if portal_type in ttool.objectIds():
        if display_cache.has_key(portal_type):
            display_as_document_in_listing = display_cache[portal_type]
        else:
            display_as_document_in_listing = getattr(ttool[portal_type],
                                                     'cps_display_as_document_in_listing',
                                                     None)
            display_cache[portal_type] = display_as_document_in_listing
    else:
        display_as_document_in_listing = 0

    if hide_folder and (item.isPrincipiaFolderish and not display_as_document_in_listing):
       continue

    if displayed != [''] and item.portal_type not in displayed:
        continue
    review_state = wtool.getInfoFor(item, 'review_state', 'nostate')
    if review_state == 'published':
        if not mtool.checkPermission('Modify portal content', item):
            doc = item.getContent()
            if now < doc.effective() or now > doc.expires():
                continue

    filtered_items.append(item)

# sorting
# XXX hardcoded status !
status_sort_order={'nostate':'0',
                   'pending':'1',
                   'published':'2',
                   'work':'3',
                   }

# XXX these methods should return a tuple and not some half-baked string.
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

def author_sortkey(a):
    return str(not a.isPrincipiaFolderish) + \
           str(wtool.getInfoFor(a,'actor','')) + \
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
elif sort_by == 'author':
    make_sortkey = author_sortkey

objects = [ ( make_sortkey(x), x ) for x in filtered_items ]

if direction == 'desc':
    # XXX Using a sort method is slow, better reverse at the end.
    objects.sort(cmp_desc)
elif direction == 'asc':
    objects.sort() # tuples compare "lexicographically"
else:
    pass

filtered_items = [ x[1] for x in objects ]

return filtered_items
