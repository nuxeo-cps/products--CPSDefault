# Copyright 2003 Nuxeo SARL <http://www.nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

"""CMFCalendar portal_calendar tool patch relying on CPSDefault's
search script (not on portal_catalogue)

$Id$
"""

from Products.CMFCalendar import CalendarTool

from DateTime import DateTime
import calendar

from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from zLOG import LOG, DEBUG

security = ClassSecurityInfo()

security.declarePublic('catalog_getcpsevents')
def catalog_getcpsevents(self, year, month, location=None, event_types=None):
    """ given a year and month return a list of days that have events """
    
    last_day=calendar.monthrange(year, month)[1]
    nb_days=calendar.monthrange(year, month)[1]
    first_date = DateTime(str(month)+'/1/'+str(year)+ ' 12:00:00AM')
    last_date = DateTime(str(month)+'/'+str(nb_days)+'/'+str(year)+ ' 23:59:59AM')

    final_event_types = self.calendar_types
    if event_types:
        final_event_types = event_types

    query = self.search(query={'portal_type':final_event_types,
                               'review_state':'published',
                               },
                        folder_prefix=location,
                        start_date=first_date,end_date=last_date)

    # compile a list of the days that have events
    eventDays={}
    for daynumber in range(1, 32): # 1 to 31
        eventDays[daynumber] = {'eventslist':[], 'event':0, 'day':daynumber}
    for q in query:
        result = q.getObject().getContent()
        if callable(result.start):
            sd = result.start()
        else:
            sd = result.start
        if callable(result.end):
            ed = result.end()
        else:
            ed = result.end

        event={}
        # we need to deal with events that end next month
        if  ed.month() != month:  # doesn't work for events that last ~12 months - fix it if it's a problem, otherwise ignore
            eventEndDay = last_day
            event['end'] = None
        else:
            eventEndDay = ed.day()
            event['end'] = ed.Time()
        # and events that started last month
        if sd.month() != month:  # same as above re: 12 month thing
            eventStartDay = 1
            event['start'] = None
        else:
            eventStartDay = sd.day()
            event['start'] = sd.Time()
        event['title'] = result.Title or result.id
        if eventStartDay != eventEndDay:
            allEventDays = range(eventStartDay, eventEndDay+1)
            eventDays[eventStartDay]['eventslist'].append({'end':None, 'start':sd.Time(), 'title':result.Title})
            eventDays[eventStartDay]['event'] = 1
            for eventday in allEventDays[1:-1]:
                eventDays[eventday]['eventslist'].append({'end':None, 'start':None, 'title':result.Title})
                eventDays[eventday]['event'] = 1
            eventDays[eventEndDay]['eventslist'].append({'end':ed.Time(), 'start':None, 'title':result.Title})
            eventDays[eventEndDay]['event'] = 1
        else:
            eventDays[eventStartDay]['eventslist'].append(event)
            eventDays[eventStartDay]['event'] = 1

    return eventDays

security.declarePublic('getCPSEventsForCalendar')
def getCPSEventsForCalendar(self, month='1', year='2002', location=None,
                            event_types=None):
    """ recreates a sequence of weeks, by days each day is a mapping.
    {'day': #, 'url': None}
    """

    #check locale in order to set 1st weekday correctly (not done at import time
    #as in CMFCalendar as the locale depends on Localizer and can change at any
    #point in time (it is not dependant on the system locale)
    if getToolByName(self,'Localizer').get_selected_language().startswith('en'):
        calendar.setfirstweekday(6)
    else:
        calendar.setfirstweekday(0)
        
    year=int(year)
    month=int(month)
    # daysByWeek is a list of days inside a list of weeks, like so:
    # [[0, 1, 2, 3, 4, 5, 6],
    #  [7, 8, 9, 10, 11, 12, 13],
    #  [14, 15, 16, 17, 18, 19, 20],
    #  [21, 22, 23, 24, 25, 26, 27],
    #  [28, 29, 30, 31, 0, 0, 0]]
    daysByWeek=calendar.monthcalendar(year, month)
    weeks=[]

    events=self.catalog_getcpsevents(year, month, location, event_types)

    for week in daysByWeek:
        days=[]
        for day in week:
            if events.has_key(day):
                days.append(events[day])
            else:
                days.append({'day': day, 'event': 0, 'eventslist':[]})

        weeks.append(days)

    return weeks


security.declarePublic('getCPSEventsForThisDay')
def getCPSEventsForThisDay(self, thisDay, location=None, event_types=None):
    """ given an exact day return ALL events that:
    A) Start on this day  OR
    B) End on this day  OR
    C) Start before this day  AND  end after this day"""

    first_date, last_date = self.getBeginAndEndTimes(thisDay.day(),
                                                     thisDay.month(),
                                                     thisDay.year())

    if event_types:
        final_event_types = event_types.split(',')
    else:
        final_event_types = self.calendar_types

    results = self.search(query={'portal_type': final_event_types,
                                 'review_state': 'published',
                                 'sort-on': 'start',
                                 'start': {'query': last_date,
                                           'range': 'max'},
                                 'end': {'query': first_date,
                                         'range': 'min'},
                                 },
                          folder_prefix=location,)


    return results

security.declarePublic('getDayList')
def getDayList(self,localizer):
    """ Returns a list of days with the correct start day first """
    if localizer.get_selected_language().startswith('en'):
        return ['6','0','1','2','3','4','5']
    else:
        return ['0','1','2','3','4','5','6']

#Adding methods to class CalendarTool
CalendarTool.CalendarTool.getCPSEventsForCalendar = getCPSEventsForCalendar
CalendarTool.CalendarTool.catalog_getcpsevents = catalog_getcpsevents
CalendarTool.CalendarTool.getCPSEventsForThisDay = getCPSEventsForThisDay
CalendarTool.CalendarTool.getDayList = getDayList

