##parameters=event=None, which_date='start_date'
# $Id$
""" returns a formatted start/end date from a document
    implementing the event interface
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
