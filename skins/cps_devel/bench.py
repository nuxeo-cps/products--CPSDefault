## Script (Python) "bench"
##parameters=obj=None, iteration=50, **kw
##title=Bench
##$Id$
"""
require External method Benchmarktimer installed by cpsintall
set BENCHMARKTIMER_LEVEL in your start script
to benchmark an object http://server/foo/bar run:
http://server/foo/bar/bench
to bench a zpt or a python script
http://server/bench?foo/bar
"""
if obj is None:
    ob_rurl=context.REQUEST.environ.get('QUERY_STRING')
    if ob_rurl:
        obj = context
        ob_rpath = tuple(ob_rurl.split('/'))
        for elem in ob_rpath:
            if elem and elem not in ['view']:
#                print 'traversing to ', elem, '<br>'
                obj=getattr(obj, elem)
    else:
        obj=context

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
    return bmt.getProfiling() + '<hr>last exec result:<br>' + str(ret)

context.REQUEST.RESPONSE.setHeader('content-type', 'text/html')
print '<h3>bench python script</h3>'
print '<b>making %s iteration of %s</b><br>' % (iteration, obj.getId())
print 'Started:', DateTime(), '<hr>'
print bench()

return printed
