## Script (Python) "getBatchList"
##parameters=items=[], columns=1, items_per_page=10
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


# Fetching Localizer message catalog
portal = context.portal_url.getPortalObject()
mcat = portal.Localizer.default

#
# Now the page results link
#

if len(items) == 0:
    return batches, None, None

batch_string = ""

# Calculate the number of pages
nb_pages = len(items) / items_per_page
if not same_type(nb_pages, 1):
    nb_pages = int(nb_pages) + 1

# Then loop over the number of pages
# and construct the page link

j = 0           # for the nb of items
current = [0,1] # for the current position in the search

for i in range(nb_pages):
    if b_start != j:
        batch_string += """<a href="%s" >%s</a>&nbsp;""" \
                        %( context.REQUEST.BASE5+"?b_start:int="+str(int(j)),
                           str(i+1) )
    else:
        current = [i+1,j]
        batch_string += str(i+1)+"&nbsp;"
    j += items_per_page

# Adding the previous link if we are not at the beginning of the file
if current[0] > 1:
    batch_string = """<a href="%s" >%s</a>&nbsp;""" \
                   %( context.REQUEST.BASE5+"?b_start:int=" + \
                      str(int(current[1] - items_per_page)) , \
                      mcat("batch_previous")) + batch_string

# Adding the next link if we are not at the end of the list
if current[0] != nb_pages:
    batch_string += """<a href="%s" >%s</a>&nbsp;""" \
                    %( context.REQUEST.BASE5+"?b_start:int=" + \
                       str(int(current[1] + items_per_page)) , \
                       mcat("batch_next"))

# Test if we are on the last page
limit = int(b_start + items_per_page)
if  limit > len(items):
    limit = len(items)

info_string = mcat("%s - %s of %s" \
                   %(b_start+1, limit, len(items)))

batch_string = mcat('label_page')+"&nbsp;" + batch_string

return batches, batch_string, info_string
