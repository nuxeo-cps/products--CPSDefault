##parameters=only_ids=0
# $Id$
"""
FIXME: add docstring.

only_ids is set when you just want a list of portal types
(e.g. for search.py)
"""

ttool = context.portal_types

searchable = []

for ti in ttool.listTypeInfo():
    if ti.getProperty('cps_is_searchable', 0):
        if only_ids:
            searchable.append(ti.getId())
        else:
            searchable.append(ti)

return searchable
