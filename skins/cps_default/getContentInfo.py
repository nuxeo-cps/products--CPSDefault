## Script (Python) "getContentInfo"
##parameters=proxy=None, doc=None, level=0
##title=Get content info used by macros
## $Id$
""" Return information about a content item (ie a proxy)
level: 0 (default cost 1)
  id, title, title_or_id, review_state, icon, rev, lang, stime
level: 1 (cost 1.3)
  level 0 + descr, size
level: 2 (cost 4.6)
  level 1 + states
level: 3 (cost 7)
  level 2 + history
"""
if not proxy:
    proxy = context

bmt = context.Benchmarktimer('getContentInfo for ' + proxy.id,
                             level=-3)
bmt.setMarker('start')

wtool=context.portal_workflow

def compute_states(no_history=0):
    ptool=context.portal_proxies
    ttool=context.portal_trees
    folders_info = {}

    for tree in ttool.objectValues():
        for f in tree.getList(filter=0):
            folders_info[f['rpath']] = f

    wf_vars = ['review_state', 'time']
    if not no_history:
        wf_vars.append('review_history')
    proxies_info = ptool.getProxyInfosFromDocid(context.getDocid(),
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
             'time': px['time'],
             'stime': px['time'].aCommon(), # XXX TODO: i18n
             }
        states.append(d)
        for d in px.get('review_history') or ():
            if not (d.has_key('actor')
                    and d.has_key('time')
                    and d.has_key('action')):
                continue
            d['stime']=d['time'].aCommon() # XXX TODO: i18n            
            d['section_title'] = folder_title
            history.append(d)

    def cmp_rs(a, b):
        return -cmp(a['review_state'], b['review_state'])
    states.sort(cmp_rs)

    def cmp_date(a, b):
        return -cmp(a['time'], b['time'])
    history.sort(cmp_date)

    return states, history


# basic information level 0
info={}
info['title_or_id']=proxy.title_or_id()
info['title']=proxy.Title()
info['id']=proxy.id
info['icon']=proxy.getIcon()
info['type']=proxy.getPortalTypeName()
info['review_state']=wtool.getInfoFor(proxy, 'review_state', '')
langrev = proxy.getLanguageRevisions()
info['rev']=langrev.values()[0]
info['lang']=langrev.keys()[0]
info['time']=wtool.getInfoFor(proxy, 'time', '')
if info['time']:
    info['stime']=info['time'].aCommon() # XXX i18n
else:
    info['stime']=''

# level 1
if level > 0:
    if not doc:
        doc = proxy.getContent()
    info['description'] = doc.Description()
    if hasattr(doc, 'get_size'):
        try:
            info['size'] = doc.get_size()
        except:
            pass

# level 2
if level == 2:
    info['states'], None = compute_states(1)

# level 3
if level > 2:
    info['states'], info['history'] = compute_states()

info['level']=level

bmt.setMarker('stop')
bmt.saveProfile(context.REQUEST)
return info
