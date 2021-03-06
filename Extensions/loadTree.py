## Script (Python) "loadTree"
##title=import tree from a configuration file
##parameters=
## $Id$
"""
build a tree using a data file created with skin/cps_devel/dump_tree
the file should be located in CLIENT_HOME (ie $ZS/var folder)
"""
import os
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from zLOG import LOG, INFO, DEBUG
from Products.CMFCore.utils import getToolByName
from Products.CPSCore.utils import makeId
from Products.CPSCore.EventServiceTool import getEventService

def pr(bla):
    if (bla):
        LOG('loadTree:', INFO, bla)


metadata_fields = ['Title', 'Description']

class DataConfig:
    parser = None
    filename = ''
    sep = '|'

    def __init__(self, filename):
        self.filename = filename
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
        return self.getList(folder, 'contents')

    def getPermission(self, folder='root'):
        return self.getList(folder, 'permission')

def createContent(portal, type, path, id, force=None, **kw):
    if path:
        path = path[1:]
        pr('check %s/%s' % (path, id))

    evtool = getEventService(portal)
    portal_types = getToolByName(portal, 'portal_types')

    parent = portal.unrestrictedTraverse(path)

    ti = None
    is_proxy = None
    for t in portal_types.listTypeInfo():
        if t.getId() == type:
            ti = t
            break
    if ti:
        is_proxy = hasattr(ti, 'cps_proxy_type') and ti.cps_proxy_type != ''

    #dbg display ti info find builder
    if id in parent.objectIds():
        pr('\t%s already created' % id)
        if not force:
            return
        pr('\tforcing kw:%s' % str(kw))
    else:
        pr('\tcreate %s id:%s kw:%s' % (
            type, id, str(kw)))
        if is_proxy:
            parent.invokeFactory(type, id)
        elif is_proxy == 0:
            apply(portal_types.constructContent,
                  (type, parent, id, None), {})
        elif is_proxy is None:
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
    if is_proxy:
        doc = ob.getEditableContent()
        doc.edit(**kw)
        evtool.notifyEvent('modify_object', parent, {})
        evtool.notifyEvent('modify_object', ob, {})
    else:
        ob.manage_changeProperties(**kw)
        ob.reindexObject()

    return ob



def buildTree(portal, cfg, parent='root', path='', parent_type=None):
    if parent != 'root':
        path += '/'+cfg.get(parent, 'id', makeId(parent, lower=1))
    parent_type = cfg.get(parent, 'type', parent_type)
    contents = cfg.getContents(parent)
    for content in contents:
        id = cfg.get(content, 'id', makeId(content, lower=1))
        type = cfg.get(content, 'type', parent_type)
        force = cfg.get(content, 'force')
        kw = cfg.getKw(content,
                       remove=('id', 'type', 'force',
                               'contents', 'permission'))
        #XXX: make first letter uppercase for some fields (metadata)
        #     as this info is somehow lost between what's output by dump_tree
        #     and this point (probably by the parser)
        for field in metadata_fields:
            lowered_field = field.lower()
            if kw.has_key(lowered_field):
                kw[field] = kw.get(lowered_field)
                del kw[lowered_field]
        #End of XXX
        ob = createContent(portal, type, path, id, force, **kw)
        if ob:
            for perm in cfg.getPermission(content):
                permission = cfg.get(perm, 'permission')
                roles = cfg.getList(perm, 'roles')
                acquire = int(cfg.get(perm, 'acquire', '0'))
                if not len(roles) or not permission:
                    continue
                ob.manage_permission(permission, roles=roles, acquire=acquire)

    for content in contents:
        buildTree(portal, cfg, content, path, parent_type)


def loadTree(self, filename='tree.ini'):
    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()
    filename = os.path.join(CLIENT_HOME, filename)
    pr('INITIALIZING TREE with %s' % (filename))
    cfg = DataConfig(filename)
    buildTree(portal, cfg)
    pr('END')

    return 'loadTree %s Done.' % filename
