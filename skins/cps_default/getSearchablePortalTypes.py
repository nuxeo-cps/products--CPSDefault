##parameters=only_ids=0
# $Id$
""" Only_ids is set when you just want a list of portal types
(e.g. for search.py) """

ttool = context.portal_types

searchable = []

for ti in ttool.listTypeInfo():
    if hasattr(ti, 'cps_is_searchable') and ti.cps_is_searchable:
        if only_ids:
            searchable.append(ti.getId())
        else:
            searchable.append(ti)

return searchable
