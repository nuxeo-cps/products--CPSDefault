##parameters=only_ids=0

# only_ids is set when you just want a list of portal types
# (e.g. for search.py)

ttool = context.portal_types

searchable = []

for ti in ttool.listTypeInfo():
    if ti.getActionById('issearchabledocument', None):
        if only_ids:
          searchable.append(ti.getId())
        else
          searchable.append({'id': ti.getId(), 'title': ti.Title()})

return searchable
