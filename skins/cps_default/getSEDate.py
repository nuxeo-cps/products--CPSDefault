##parameters=event=None, which_date='start_date'
# $Id$
"""
Returns a formatted start/end date from a document implementing the event
interface.

FIXME: what is 'which_date'? What does 'SE' mean in the method's name? 
"""

dt = None
if event:
    if which_date == 'start':
        dt = event.getContent().start()
    elif which_date == 'end':
        dt = event.getContent().end()
        
if dt:
    return context.getDateStr(dt, 'short')
else:
    return ''
