##parameters=context_url,datestring,location,event_types
# $Id$
"""
Compute the correct list of URL parameters for calendar_cpsday_view
"""

from urllib import urlencode

args = {'date': datestring}

if location and not location.isspace():
    args['location'] = location

if event_types:
    args['event_types'] = ','.join(event_types)

return context_url + '/calendar_cpsday_view?' + urlencode(args)
