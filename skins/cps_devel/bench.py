## Script (Python) "bench"
##parameters=obj=None, iteration=50, **kw
##title=Bench
##$Id$
"""
see doc/HOWTO.BENCHMARK
"""
if obj is None:
    obj = context
    obj_rurl=context.REQUEST.environ.get('QUERY_STRING')
    if obj_rurl:
        obj_rpath = tuple(obj_rurl.split('/'))
        for elem in obj_rpath:
            if elem and elem not in ['view']:
                #print 'traversing to ', elem, '<br />'
                obj=getattr(obj, elem)

def bench():
    bmt = context.Benchmarktimer(obj.getId())
    if not bmt.in_bench():
        raise 'Benchmarktimer not available'
    bmt.setMarker('first exec start')
    obj(**kw) # don't take into account the first execution
    bmt.setMarker('first exec stop ')
    bmt.setMarker('iteration  start')

    for i in range(iteration):
        obj(**kw)

    bmt.setMarker('iteration  stop ')
    bmt.setMarker('last exec  start')
    ret = obj(**kw)
    bmt.setMarker('last exec  stop ')                   
    return bmt.getProfiling() + '<hr />last exec result:<br />' + str(ret)

context.REQUEST.RESPONSE.setHeader('content-type', 'text/html')
print '<h3>bench python script</h3>'
print '<strong>making %s iterations of %s</strong><br />' % (iteration, obj.getId())
print 'Started:', DateTime(), '<hr />'
print bench()

return printed
