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
        return '\n'.join(_log)
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
    

def makeId(title):
    id = title.lower()
    id = id.replace(' ', '_')
    id = id.replace(',', '')
    id = id.replace('é', 'e')
    id = id.replace('à', 'a')
    id = id.replace('ç', 'c')
    id = id.replace('è', 'e')
    id = id.replace('&', '-')    
    return id.lower()


def createContent(type, path, id, title, desc='', force=None, **kw):
    if path:
        path = path[1:]
        pr('check %s/%s' % (path, id))
    parent = portal.unrestrictedTraverse(path)
    if id in parent.objectIds():
        pr('\t%s already created' % id)
        if not force:
            return
        pr('\tforcing title %s desc:%s and %s' % (title, desc, str(kw)))
    else:
        pr('\tcreate %s id:%s title:%s desc:%s and %s' % (type, id, title,
                                                          desc, str(kw)))
        if type == 'folder':
            parent.manage_addPortalFolder(id, title)
        else:
            parent.invokeFactory(type, id)
    if type == 'folder':
        return
    ob = getattr(parent, id)
    ti = ob.getTypeInfo()
    if ti is None:
        raise Exception('No portal type found for box: %s' % ob.getId())
    proxy_type = ti.getActionById('isproxytype', None)
    if proxy_type:
        doc = ob.getEditableContent()
        doc.edit(title=title, description=desc, **kw)
        portal_eventservice.notifyEvent('modify_object', parent, {})
        portal_eventservice.notifyEvent('modify_object', ob, {})
    else:
        ob.manage_changeProperties(title=title, description=desc, **kw)
        ob.reindexObject()


def buildTree(cfg, parent='root', path='', parent_type=None):
    if parent != 'root':
        path += '/'+cfg.get(parent, 'id', makeId(parent))
    parent_type = cfg.get(parent, 'type', parent_type)
    contents = cfg.getContents(parent)
    for content in contents:
        id = cfg.get(content, 'id', makeId(content))
        title = cfg.get(content, 'title', content)
        type = cfg.get(content, 'type', parent_type)
        desc = cfg.get(content, 'desc')
        force = cfg.get(content, 'force')
        kw = cfg.getKw(content,
                       remove=('id', 'title', 'type',
                               'desc', 'force', 'contents'))
        createContent(type, path, id, title, desc, force, **kw)

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

