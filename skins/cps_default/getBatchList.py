## Script (Python) "getBatchList"
##parameters=items=[], columns=1, items_per_page=10, zoom=0
# $Id$
"""
Given the desired number of colums, constructs a list of batches to render
as much columns as necessary within a single macro.
As well, return the page results link to display straight for the navigation
"""

from math import ceil
from ZTUtils import Batch

#
# First constructing the batch
#

len_items = len(items)

# desperately empty, no need to go further
if not len_items:
    return [], {}, []

b_start = int(context.REQUEST.get('b_start', 0))

# extract the n first items in a zoomed list
zoomed = []
if not b_start and zoom:
    zoom = int(zoom)
    zoomed = Batch(items[:zoom], zoom, 0)
    n = len_items - zoom
    # deal with items left
    items = items[zoom:]

items_per_page = float(items_per_page)
size = int(ceil(items_per_page / columns))

b1 = Batch(items, size, b_start, orphan=0)
batches = [b1]

b_next = b1
for c in range(columns - 1):
    if b_next.next:
        b_next = b_next.next
        batches.append(b_next)

#
# Now the page results parameters
#

# Calculate the number of pages
nb_pages = len_items / items_per_page
if not same_type(nb_pages, 1) and nb_pages > 1:
    nb_pages = int(nb_pages) + 1

# no more advanced arithmetics
items_per_page = int(items_per_page)

# Test if we are on the last page
limit = b_start + items_per_page
if  limit > len_items:
    limit = len_items

batch_info = {'nb_pages': nb_pages,
              'start': b_start + 1,
              'limit': limit,
              'length': len_items,
              'previous': None,
              'next': None,
                 }

# for the nb of items 
j = 0           
# for the current position in the search
current = [0, 1] 
# list of b_start values
pages = []

# Loop over the number of pages and construct the page link
for i in range(nb_pages):
    pages.append(j)
    if b_start == j:
        current = [i + 1, j]
    j += items_per_page

# list of b_start to other pages
batch_info['pages'] = pages

# if we are not at the beginning of the file
if current[0] > 1:
    batch_info['previous'] = current[1] - items_per_page

# Adding the next link if we are not at the end of the list
if current[0] != nb_pages:
    batch_info['next'] = current[1] + items_per_page

return batches, batch_info, zoomed
