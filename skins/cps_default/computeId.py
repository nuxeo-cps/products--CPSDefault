##parameters=compute_from='', max_chars_for_id=20, location=None, portal_type=None

# $Id$
"""Generate an id from a given string.

This method avoids collisions.
"""

from string import maketrans
from random import randrange
import re
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, DEBUG

GENERATION_MAX_TRIES = 500
def generateNewId(id):
    """Generate annew id.

    This is to be used to avoid collisions.
    """
    m = re.match('(.*)\d\d\d\d$', id)
    if m is not None:
        prefix = m.group(1)
    else:
        prefix = id

    tries = 0
    while 1:
        tries += 1
        if tries == GENERATION_MAX_TRIES:
            # grow prefix
            prefix = id
            tries = 0
        suffix = str(randrange(1000, 10000))
        id = prefix + suffix
        return id


# Initialization
id = compute_from

# Normalization
id = id.replace('Æ', 'AE')
id = id.replace('æ', 'ae')
id = id.replace('¼', 'OE')
id = id.replace('½', 'oe')
id = id.replace('ß', 'ss')
tr = maketrans(
    r"'\;/ &:ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜİàáâãäåçèéêëìíîïñòóôõöøùúûüıÿ",
    r'_______AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyy')
id = id.translate(tr)
ok_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.'
id = ''.join([c for c in id if c in ok_chars])
id = id.lower()

# Avoiding duplication of meaningless chars
id = re.sub('-+', '-', id)
id = re.sub('_+', '_', id)
id = re.sub('\.+', '.', id)

# Avoiding annoying presence of meaningless chars
while id.startswith('-') or id.startswith('_') or id.startswith('.'):
    id = id[1:]
while id.endswith('-') or id.endswith('_') or id.endswith('.'):
    id = id[:-1]

# Fallback if empty
if not id:
    id = str(int(DateTime())) + str(randrange(1000, 10000))

# Word splitting
# The following regexp split the given id into words separated by the following
# separators: '-' '_' '.'
words = re.split('-*_*\.*\s*', id)

# Removing meaningless words according to the current locale.
#locale = self.Localizer.get_selected_language()
cpsmcat = context.Localizer.default
words_meaningless = cpsmcat('words_meaningless')
words = [w for w in words if w not in words_meaningless]

# Preventing word cuts
id = words[0] # The id needs to contain at least one word
words = words[1:]
while words and ((len(id) + len(words[0]) + 1) <= max_chars_for_id):
    id = "%s_%s" % (id, words[0])
    words = words[1:]

# Get the container in which we want the new object to be created.
if location is not None:
    container = location
else:
    container = context.this()

# Ensuring that the id is not a portal reserved id (this is a case where
# acquisition is a pain) and that the id is not used in the given container.
portal = getToolByName(context, 'portal_url').getPortalObject()
# It's needed to allow index_html for join code
while (hasattr(portal, id)
       and id not in ('index_html', 'sections', 'workspaces')
       or hasattr(container.aq_explicit, id)):
    # The id is reserved we need to compute another id
    id = generateNewId(id)

return id
