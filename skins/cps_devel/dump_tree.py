## Script (Python) "dump_tree.py"
##parameters=
##


types = ['Workspace', 'Section', 'CPS Boxes Container',
         'Base Box', 'Content Box', 'Tree Box', 'Action Box', 'Text Box']

black_list = ['.cps_workflow_configuration']


def dump_it(obj, level=-1):
    s = ''
    type = obj.getPortalTypeName()
    if not type in types:
        return s
    if obj.id in black_list:
        return s
    level += 1
    s += '# level %d\n' % (level + 1)
    s += '[%s]\n' % obj.absolute_url(1)
    s += 'id = %s\n' % obj.id
    s += 'type = %s\n' % type
    if not hasattr(obj, 'title') and hasattr(obj, 'Title') and obj.Title():
        s += 'title = %s\n' % obj.Title()


    ti = obj.getTypeInfo()
    is_proxy = hasattr(ti, 'cps_proxy_type') and ti.cps_proxy_type != ''

    if is_proxy:
        doc = obj.getContent()
    else:
        doc = obj

#    s += "param = %s" % str(doc.propdict())
    params = doc.propdict()
    for param in params.keys():
        val = getattr(doc, param)
        if callable(val):
            val = val()
        param_type = params[param]['type']
        if val:
            if param_type == 'lines':
                if same_type(val, []) or same_type(val, ()):
                    val = '\n  '.join(val)
                else:
                    val = str(val)
                    val = val.replace('\n', '\n  ')
            s += '%s = %s\n' % (param, str(val))
        elif param_type == 'boolean':
            s += '%s =\n' % param
        elif param_type == 'int':
            s += '%s = 0\n' % param


    if obj.isPrincipiaFolderish:
        ss = ''
        l = []
        for o in obj.objectValues():
            ret = dump_it(o, level)
            if ret:
                ss += ret
                l.append(o.absolute_url(1))
        if len(l):
            s += 'contents = %s\n\n' % '|'.join(l)
            s += ss

    s += '\n'
    level -=1
    return s

s = dump_it(context)


            #d = o.getContent()
#        if hasattr(d, 'dump_data'):
#            print 'dump_data = %s' % d.dump_data()
#        if o.isPrincipiaFolderish():
#            dump_it(o)

return  '## dump_data %s:\n\n%s' % (context.absolute_url(1), s)
