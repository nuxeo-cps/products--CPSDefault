##parameters=items, columns=1, items_per_page=10.0

""" given the desired number of colums, constructs a list of batches to render
as much columns as necessary within a single macro. """

# some math involved ;)
from math import ceil
from ZTUtils import Batch

# the list of batches to fill columns with
batches = []

# be sure to use a float value for having a decimal result
items_per_page = float(items_per_page)
size = int(ceil(items_per_page / columns))

# the classical batch start value updated when moving from a page to another
b_start = int(context.REQUEST.get('b_start', 0))

# first default batch makes first column
b1 = Batch(items, size, int(b_start), orphan=0)
batches.append(b1)

# computing other batches for the remaining columns
b_next = b1
for c in range(columns - 1):
    # if another batch is possible
    if b_next.next:
        b_next = b_next.next
        batches.append(b_next)
    else:
        # no more batch possible
        break

# columns are now full or the item list was empty before
return batches
