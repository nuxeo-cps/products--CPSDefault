##parameters=key=None
#$Id$
"""Return a portal type vocabulary, used as MethodVocabulary."""

types = context.getSortedContentTypes(allowed=0)
l10n = context.translation_service
res = [(item.getId(), l10n(item.Title()))
       for item in types]
if key is not None:
    res = [item[1] for item in res if item[0] == key][0]

return res
