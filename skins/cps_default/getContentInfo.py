
##parameters=proxy=None, doc=None, level=0, cpsmcat=None
# $Id$
"""
Return information about a content item (ie a proxy)

level: 0 (default cost 1)
  id, title, title_or_id, review_state, icon, rev, lang, type
  time_str, creator, rpath, url
level: 1 (cost 1.3)
  level 0 + descr, size + doc + additional information from obj
level: 2 (cost 4.6)
  level 1 + states
level: 3 (cost 7)
  level 2 + history
level: 4 (cost ???)
  level 3 + archived
"""

import logging
logger = logging.getLogger('Script (Python) getContentInfo:')
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized

# how many characters for the description
DESCRIPTION_MAX_LENGTH = 150

if cpsmcat is None:
    cpsmcat = context.translation_service

if proxy is None:
    proxy = context

wtool = getToolByName(context, 'portal_workflow')
utool = getToolByName(context, 'portal_url')
ptool = getToolByName(context, 'portal_proxies')
mtool = getToolByName(context, 'portal_membership')
portal = utool.getPortalObject()

rpath = None
if hasattr(proxy.aq_explicit, 'getRID'):
    # this is a brain
    # rpath is build with catalog path that include languageView selection

    # FIXME: something is broken here when using virtual host monsters
    rpath = utool.getRpathFromPath(proxy.getPath())

    # change view to switch to have a sticky behaviour
    from Products.CPSCore.utils import KEYWORD_SWITCH_LANGUAGE, \
         KEYWORD_VIEW_LANGUAGE
    rpath = rpath.replace(KEYWORD_VIEW_LANGUAGE, KEYWORD_SWITCH_LANGUAGE)
    proxy = proxy.getObject()

bmt = getattr(portal, 'Benchmarktimer', None)
if bmt is not None:
    bmt = bmt('getContentInfo for ' + proxy.getId(), level=-3)
    bmt.setMarker('start')

def getRpathTitle(rpath):
    """Get object's title, or None if Unauthorized or nonexisting."""
    try:
        ob = portal.restrictedTraverse(rpath, None)
        if ob is None:
            return None
        return ob.Title()
    except Unauthorized:
        return None


def compute_states(no_history=0):
    wf_vars = ['review_state', 'time']
    docid = proxy.getDocid()
    if docid:
        proxies_info = ptool.getProxyInfosFromDocid(docid,
                                                    workflow_vars=wf_vars)
    else:
        # Not a proxy
        ob_info = {
            'rpath': utool.getRpath(proxy),
            'language_revs': {'en': 0},
            'visible': mtool.checkPermission('View', proxy),
            }
        for var in wf_vars:
            ob_info[var] = wtool.getInfoFor(proxy, var, None)
        proxies_info = [ob_info]
    states = []
    for proxy_info in proxies_info:
        # take in account only accessible proxies
        if not proxy_info['visible']:
            continue

        lrpath = proxy_info['rpath'].split('/')
        folder_rpath = '/'.join(lrpath[:-1])
        folder_title = getRpathTitle(folder_rpath)
        if not folder_title:
            # Unauthorized
            if len(lrpath) > 1:
                folder_title = lrpath[-2]
            else:
                folder_title = '?'

        proxy_info_proxy = None
        portal_type = None
        if proxy_info.has_key('object'):
            proxy_info_proxy = proxy_info['object']
            if hasattr(proxy_info_proxy, 'portal_type'):
                portal_type = proxy_info_proxy.portal_type

        d = {'rpath': folder_rpath,
             'title': folder_title,
             'type': portal_type,
             'review_state': proxy_info['review_state'],
             'rev': str(proxy_info['language_revs'].values()[0]),
             'language': proxy_info['language_revs'].keys()[0],
             'time': proxy_info['time'],
             'time_str': context.getDateStr(proxy_info['time']),
             'proxy': proxy_info_proxy,
             }
        d['lang'] = d['language']       # for compatibility
        states.append(d)

    history = []
    if not no_history:
        review_history = wtool.getFullHistoryOf(proxy)
        if not review_history:
            review_history = wtool.getInfoFor(proxy, 'review_history', ())
            remove_redundant = 0
        else:
            remove_redundant = 1
        for d in review_history:
            if not (d.has_key('actor')
                    and d.has_key('time')
                    and d.has_key('action')):
                continue
            action = d['action']
            # Internal transitions hidden from the user.
            if action in ('unlock', 'checkout_draft_in'):
                continue
            # Skip redundant history (two transition when publishing).
            if action == 'copy_submit' and remove_redundant:
                continue
            # Transitions involving a destination container.
            if action in ('submit', 'copy_submit'):
                d['has_dest'] = 1
                dest_container = d.get('dest_container') or '?'
                d['dest_container'] = dest_container
                dest_title = getRpathTitle(dest_container)
                if not dest_title:
                    # Unauthorized
                    dest_title = dest_container.split('/')[-1]
                d['dest_title'] = dest_title
            d['time_str'] = context.getDateStr(d['time'])
            history.append(d)

    def cmp_rs(a, b):
        return -cmp(a['review_state'], b['review_state'])
    states.sort(cmp_rs)

    def cmp_date(a, b):
        return -cmp(a['time'], b['time'])
    history.sort(cmp_date)

    return states, history

def compute_archived():
    archived = proxy.getArchivedInfos()
    # Keep only frozen revisions.
    archived = [d for d in archived if d['is_frozen']]
    archived.reverse()
    for d in archived:
        d['time_str'] = context.getDateStr(d['modified'])
    return archived

# basic information level 0
info = {}
if rpath is None:
    info['rpath'] = utool.getRpath(proxy)
else:
    info['rpath'] = rpath

info['url'] = utool.getUrlFromRpath(info['rpath'])

info['title_or_id'] = proxy.title_or_id()
info['id'] = proxy.getId()
try:
    info['title'] = proxy.Title()
except AttributeError:
    raise AttributeError, 'invalid object: %s in %s' % (info['title_or_id'],
                                                        info['rpath'])
info['icon'] = proxy.getIcon(relative_to_portal=1)
info['type'] = proxy.getPortalTypeName()

if proxy.getTypeInfo() is not None:
    info['type_l10n'] = cpsmcat(proxy.getTypeInfo().Title())
else:
    logger.debug("problem getting Type Information for proxy %s", proxy)
    info['type_l10n'] = ''
info['review_state'] = wtool.getInfoFor(proxy, 'review_state', '')
try:
    info['rev'] = str(proxy.getRevision())
    info['lang'] = proxy.getLanguage()
except AttributeError:
    # not a proxy
    # FIXME: default lang should not be hardcoded
    info['rev'] = '0'
    info['lang'] = 'en'
info['time'] = proxy.modified()

# level 1
if level > 0:
    if doc is None:
        doc = proxy.getContent()
    info['doc'] = doc
    description = doc.Description() or ''
    if len(description) > DESCRIPTION_MAX_LENGTH:
        description = description[:DESCRIPTION_MAX_LENGTH] + '...'
    info['description'] = description
    if hasattr(doc.aq_explicit, 'get_size'):
        try:
            size = doc.get_size()
        except:
            size = 0

        if size and size < 1024:
            info['size'] = '1 K'
        elif size > 1048576:
            info['size'] = '%.02f M' % float(size/1048576.0)
        elif size:
            info['size'] = str(int(size)/1024)+' K'

    if hasattr(doc.aq_explicit, 'start'):
        if callable(doc.start):
            start = doc.start()
        else:
            start = doc.start
        if start:
            info['start'] = start
            info['start_str'] = context.getDateStr(start)

    if hasattr(doc.aq_explicit, 'end'):
        if callable(doc.end):
            end = doc.end()
        else:
            end = doc.end
        if end:
            info['end'] = end
            info['end_str'] = context.getDateStr(end)

    for dc in ('Creator', 'Rights', 'Language',
               'contributors', 'source', 'relation', 'coverage'):
        key = dc.lower()
        if key == 'contributors':
            key = 'contributor'         # this is the real DC name
        try:
            meth = getattr(doc, dc)
            if callable(meth):
                value = meth()
            else:
                value = meth
            if value and not same_type(value, ''):
                value = ', '.join(value)
            info[key] = value
        except:
            info[key] = ''

    if hasattr(doc.aq_explicit, 'hidden_folder'):
        info['hidden'] = doc.hidden_folder
    else:
        info['hidden'] = 0

    if hasattr(doc.aq_explicit, 'getAdditionalContentInfo'):
        add_info = doc.getAdditionalContentInfo(proxy)
        info.update(add_info)

    if info['review_state'] == 'published':
        now = context.ZopeTime()
        eff = doc.effective()
        exp = doc.expires()
        if now < eff:
            info['review_state'] = 'deferred'
            info['review_state_date'] = context.getDateStr(eff)
        elif now > exp:
            info['review_state'] = 'expired'
            info['review_state_date'] = context.getDateStr(exp)

# level 2
if level == 2:
    info['states'], ignore = compute_states(1)

# level 3
if level >= 3:
    info['states'], info['history'] = compute_states()

# level 4
if level >= 4:
    info['archived'] = compute_archived()

info['level'] = level
if info['time']:
    info['time_str'] = context.getDateStr(info['time'])
else:
    info['time_str'] = ''


if bmt is not None:
    bmt.setMarker('stop')
    bmt.saveProfile(context.REQUEST)

return info
