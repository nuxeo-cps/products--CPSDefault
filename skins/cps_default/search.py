## Script (Python) "search"
##parameters=params={}, REQUEST=None, **kw
##title=Get content info used by macros
# $Id$
"""
 portal_type, SearchableText, Title, et Description
 autre réponse: les index que connait le catalogue en clé et la chaîne de
 caractères ou une liste de chaînes en valeur
"""

from zLOG import LOG

if REQUEST is not None:
    kw.update(REQUEST.form)
kw.update(params)
params = kw

docinfos = []

catalog = context.portal_catalog
proxytool = context.portal_proxies
ttool = context.portal_types

okpt = context.getSearchablePortalTypes(only_ids=1)

pt = params.get('portal_type', None)
if pt:
    pt = [t for t in pt if t in okpt]
else:
    pt = okpt
params['portal_type'] = pt

# seulement parmi les "vrais" documents
# ensuite on cherchera tous les proxy qui pointent sur chacun
cps_name = str(context.portal_url(relative = 1))
params['path'] = '/'+cps_name+'/portal_repository/'

#if params.setdefault('SearchableText', '').strip():
#    results = catalog(**params)
#else:
#    results = []
results = catalog(**params)

for result in results:
    #LOG('result:', -200, str(proxytool.getProxiesFromObjectId(result.getObject().getId())))
    ob = result.getObject()
    if ob is None:
        continue
    id = ob.getId()
    infos = proxytool.getProxiesFromObjectId(id)
    for info in infos:
        proxy = info['object']
        # prevent ZCatalog desynchronization
        try:
            title = proxy.Title()
        except (AttributeError):
            continue
        rpath = info['rpath']
        docinfos.append({
            'id': id,
            'rpath': rpath,
            'title': title,
            'icon': ob.getIcon(relative_to_portal=1),
            'type': ob.portal_type,
            'modification': ob.modified().strftime('%d/%m/%Y %H:%M'),
            'description': ob.Description(),
            })

def sort_method(a, b):
    return (cmp(a['rpath'], b['rpath']) or
            cmp(a['title'], b['title']) or
            0)

docinfos.sort(sort_method)

#raise str(docinfos)
return docinfos
