##parameters=

ttool = context.portal_types
searchable = []

for ti in ttool.listTypeInfo():
    if ti.getActionById('issearchabledocument', None):
        searchable.append({'id': ti.getId(), 'title': ti.Title()})

return searchable
