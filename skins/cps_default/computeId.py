##parameters=compute_from='', max_chars_for_id=20

# $Id$
"""
Return a new id computed from compute_from
"""

from string import maketrans
from random import randrange
import re

# Create, no id, get from title
newid = compute_from.strip()[:max_chars_for_id]

# Normalize
newid = newid.replace(' ', '_')
newid = newid.replace('Æ', 'AE')
newid = newid.replace('æ', 'ae')
tr = maketrans('ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜİàáâãäåçèéêëìíîïñòóôõöøùúûüıÿ',
               'AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyy')
newid = newid.translate(tr)
ok = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.'
newid = ''.join([c for c in newid if c in ok])
while newid.startswith('_') or newid.startswith('.'):
    newid = newid[1:]

while newid.endswith('_'):
    newid = newid[:-1]

newid = newid.lower()

if not newid:
    # Fallback if empty or incorrect
    newid = str(int(DateTime())) + str(randrange(1000, 10000))
    return newid

container = context.this()
if not hasattr(container.aq_explicit, newid):
    # No collision
    return newid

# Treat collision
m = re.match('(.*)\d\d\d\d$', newid)
if m is not None:
    prefix = m.group(1)
else:
    prefix = newid

tries = 0
while 1:
    tries += 1
    if tries == 500:
        # grow prefix
        prefix = newid
        tries = 0
    suffix = str(randrange(1000, 10000))
    newid = prefix + suffix
    if not hasattr(container.aq_explicit, newid):
        # No collision
        return newid

