## Script (Python) "getCalCPSDayViewParams"
##parameters=context_url,datestring,location,event_types
# $Id$
"""Compute the correct list of URL parameters for calendar_cpsday_view"""

res = context_url + 'calendar_cpsday_view?date='+datestring

if location and not location.isspace():
    res = res + '&location=' + location

if event_types:
    res = res + '&event_types='
    for t in event_types:
        res = res + t + ','
    res = res [:-1]

return res
