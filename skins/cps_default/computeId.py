##parameters=compute_from='', max_chars_for_id=24, location=None, portal_type=None, lang=None
# $Id$
"""
Generate an id from a given string with no meaningless words inside.
"""

from Products.CPSUtil.id import generateId

# Getting the meaningless words list according to the current locale
message_catalog = context.Localizer.default
meaningless_words = message_catalog.gettext('words_meaningless', lang).split()

# Get the container in which we want the new object to be created
if location is not None:
    container = location
else:
    container = context.this()

id = generateId(compute_from, max_chars=max_chars_for_id, lower=True,
                portal_type=portal_type, meaningless_words=meaningless_words,
                container=container)

return id
