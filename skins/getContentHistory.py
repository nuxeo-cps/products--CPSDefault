## Script (Python) "getContentHistory"
##parameters=only_state=0
"""
Return information about the state and history of the document.
Takes into account all existing proxies for the document.
"""

wftool = context.portal_workflow
pxtool = context.portal_proxies
ttool = context.portal_trees

folders_info = {}
for tree in ttool.objectValues():
    for f in tree.getList(filter=0):
        folders_info[f['rpath']] = f

wf_vars = ['review_state', 'time']
if not only_state:
    wf_vars.append('review_history')
proxies_info = pxtool.getProxyInfosFromDocid(context.getDocid(),
                                             workflow_vars=wf_vars)
states = []
history = []
for px in proxies_info:
    # take in account only accessible proxies
    folder_rpath = '/'.join(px['rpath'].split('/')[:-1])
    if not folders_info.has_key(folder_rpath):
        continue
    if not folders_info[folder_rpath]['visible']:
        continue
    
    folder_id = px['rpath'].split('/')[-2]
    folder_title = folders_info.get(folder_rpath,
                                     {'title':folder_id}).get('title',
                                                              folder_id)
    d = {'rpath': folder_rpath,
         'title': folder_title,
         'review_state': px['review_state'],
         'rev': px['language_revs'].values()[0],
         'lang': px['language_revs'].keys()[0],
         'visible': px['visible'],
         'time': px['time'],
         }
    states.append(d)
    for d in px.get('review_history') or ():
        if not (d.has_key('actor')
                and d.has_key('time')
                and d.has_key('action')):
            continue
        d['section_title'] = folder_title
        history.append(d)

def cmp_rs(a, b):
    return -cmp(a['review_state'], b['review_state'])
states.sort(cmp_rs)

def cmp_date(a, b):
    return cmp(a['time'], b['time'])
history.sort(cmp_date)

return {'history': history,
        'states': states,
        }
