## Script (Python) "getBatchList"
##parameters=items=[], columns=1, items_per_page=10
# $Id$
""" given the desired number of colums, constructs a list of batches to render
as much columns as necessary within a single macro. """
from math import ceil
from ZTUtils import Batch

batches = []

items_per_page = float(items_per_page)
size = int(ceil(items_per_page / columns))

b_start = int(context.REQUEST.get('b_start', 0))

b1 = Batch(items, size, b_start, orphan=0)
empty_batch = Batch( [], 1, 1)

batches.append(b1)
b_next = b1
for c in range(columns - 1):
    if b_next.next:
        b_next = b_next.next
        batches.append(b_next)
    else:
        batches.append(empty_batch)

return batches
