##parameters=key=None, is_i18n=False
#$Id$
"""Return a portal type vocabulary, used as MethodVocabulary."""

types = context.getSortedContentTypes(allowed=0)
res = [(item['id'], item['Title']) for item in types]

if key is not None:
    res = [item[1] for item in res if item[0] == key][0]

return res
