##parameters=compute_from='', max_chars_for_id=20, location=None

# $Id$
"""
Return a new id computed from compute_from
"""

from string import maketrans
from random import randrange
import re
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, DEBUG

GENERATION_MAX_TRIES = 500
def generateNewId(newid):
    """Generate new id.

    This is to be used to avoid collisions.
    """
    m = re.match('(.*)\d\d\d\d$', newid)
    if m is not None:
        prefix = m.group(1)
    else:
        prefix = newid

    tries = 0
    while 1:
        tries += 1
        if tries == GENERATION_MAX_TRIES:
            # grow prefix
            prefix = newid
            tries = 0
        suffix = str(randrange(1000, 10000))
        newid = prefix + suffix
        return newid


# Create, no id, get from title
newid = compute_from.strip()[:max_chars_for_id]

# Normalization
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

if newid:
    newid = newid.lower()
else:
    # Fallback if empty
    newid = str(int(DateTime())) + str(randrange(1000, 10000))


# Get the container in which we want the new object to be created.
if location:
    container = location
else:
    container = context.this()

# Ensuring that the id is not a portal reserved id (this is a case where
# acquisition is a pain) and that the id is not used in the given container.
portal = getToolByName(context, 'portal_url').getPortalObject()
# It's needed to allow index_html for join code
while (hasattr(portal, newid)
       and newid not in ('index_html', 'sections', 'workspaces')
       or hasattr(container.aq_explicit, newid)):
    # The id is reserved we need to compute another id
    newid = generateNewId(newid)

return newid

