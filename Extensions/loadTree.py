## Script (Python) "importData"
##title=import data from a configuration file
##parameters=
## $Id$
"""
importData see test_importData.ini for example
"""
import os
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from zLOG import LOG, INFO, DEBUG
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base


product_name='MCI'
filename='data.ini'


_log=[]
def pr(bla, _log=_log):
    if bla == 'flush':
        return '<html><head><title>IMORT DATA</title></head><body><pre>' + \
               '\n'.join(_log) + '</body></html>'
    _log.append(bla)
    if (bla):
        LOG('importData:', INFO, bla)


class DataConfig:
    parser = None
    filename = ''
    sep = '|'

    def __init__(self, filename):
        self.filename=filename
        fh = open(filename, 'r')
        parser = ConfigParser()
        parser.readfp(fh)
        fh.close()
        self.parser = parser

    def get(self, section, option, default=None):
        try:
            value = self.parser.get(section, option)
        except (NoSectionError, NoOptionError):
            return default
        return value

    def getList(self, section, option, default=''):
        value = self.get(section, option, default)
        value = [x.strip() for x in value.split(self.sep)]
        return filter(None, value)

    def getKw(self, section, remove=[]):
        kw = {}
        try:
            options = self.parser.options(section)
        except (NoSectionError, NoOptionError):
            return kw
        options = [x for x in options if x not in remove]
        for option in options:
            kw[option] = self.parser.get(section, option)
        return kw

    def getContents(self, folder='root'):
        return cfg.getList(folder, 'contents', '')

    def getPermission(self, folder='root'):
        return cfg.getList(folder, 'permission', '')


def makeId(title):
    id = title.lower()
    id = id.replace(' ', '_')
    id = id.replace(',', '')
    id = id.replace('é', 'e')
    id = id.replace('à', 'a')
    id = id.replace('ç', 'c')
    id = id.replace('è', 'e')
    id = id.replace('&', '-')
    id = id.replace('\'', '_')
    id = id.replace('/', '_')
    id = id.replace('\\', '_')
    return id.lower()


def createContent(type, path, id, force=None, **kw):
    if path:
        path = path[1:]
        pr('check %s/%s' % (path, id))
    parent = portal.unrestrictedTraverse(path)

    ttool = getToolByName(parent, 'portal_types')
    ti = None
    proxy_type = None
    for t in ttool.listTypeInfo():
        if t.getId() == type:
            ti = t
            break
    if ti:
        proxy_type = ti.getActionById('isproxytype', 0)

    #dbg display ti info find builder
    if id in parent.objectIds():
        pr('\t%s already created' % id)
        if not force:
            return
        pr('\tforcing kw:%s' % str(kw))
    else:
        pr('\tcreate %s id:%s kw:%s' % (
            type, id, str(kw)))
        if proxy_type:
            parent.invokeFactory(type, id)
        elif proxy_type == 0:
            apply(ttool.constructContent,
                  (type, parent, id, None), {})
        elif proxy_type is None:
            all_types = parent.filtered_meta_types()
            ti = None
            for t in all_types:
                if t['name'] == type:
                    ti = t
                    break
            if ti is None:
                raise 'No meta type info for type %s' % type
            # XXX: ouch there must be another way...
            meth_name = ti['action'].split('/')[-1]
            cmd = 'parent.manage_addProduct[\'%s\'].%s(id)' % (
                ti['product'], meth_name)
            pr('executing %s' % cmd)
            eval(cmd)

    ob = getattr(parent, id)
    if proxy_type:
        doc = ob.getEditableContent()
        doc.edit(**kw)
        portal_eventservice.notifyEvent('modify_object', parent, {})
        portal_eventservice.notifyEvent('modify_object', ob, {})
    else:
        ob.manage_changeProperties(**kw)
        ob.reindexObject()

    return ob



def buildTree(cfg, parent='root', path='', parent_type=None):
    if parent != 'root':
        path += '/'+cfg.get(parent, 'id', makeId(parent))
    parent_type = cfg.get(parent, 'type', parent_type)
    contents = cfg.getContents(parent)
    for content in contents:
        id = cfg.get(content, 'id', makeId(content))
        type = cfg.get(content, 'type', parent_type)
        force = cfg.get(content, 'force')
        kw = cfg.getKw(content,
                       remove=('id', 'type', 'force',
                               'contents', 'permission'))
        ob = createContent(type, path, id, force, **kw)
        if ob:
            for perm in cfg.getPermission(content):
                permission = cfg.get(perm, 'permission')
                roles=cfg.getList(perm, 'roles')
                acquire=int(cfg.get(perm, 'acquire', '0'))
                if not len(roles) or not permission:
                    continue
                ob.manage_permission(permission, roles=roles,
                                     acquire=acquire)

    for content in contents:
        buildTree(cfg, content, path, parent_type)


def main(self):
    global _log, cfg, portal, portal_url, portal_workflow, portal_eventservice
    global product_name, filename
    portal_url = getToolByName(self, 'portal_url')
    portal_workflow = getToolByName(self, 'portal_workflow')
    portal_eventservice = getToolByName(self, 'portal_eventservice')
    portal = portal_url.getPortalObject()
    filename = 'data.ini'
    app=self.getPhysicalRoot()
    p=getattr(app.Control_Panel.Products, product_name)
    filename = os.path.join(p.home + '/Extensions/', filename)
    cfg=DataConfig(filename)

    pr('INITIALIZING %s TREE with %s:' % (product_name, filename))
    buildTree(cfg)
    return pr('flush')
