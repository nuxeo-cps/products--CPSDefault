
""" CMFCalendar portal_calendar tool patch relying on CPSDefault's
search script (not on portal_catalogue)

$Id$
"""

from Products.CMFCalendar import CalendarTool

from DateTime import DateTime
import calendar
#XXX: the following is interesting but should depend on the locale
#so we cannot do it here
#calendar.setfirstweekday(6) #start day  Mon(0)-Sun(6)

from AccessControl import ClassSecurityInfo

from zLOG import LOG, DEBUG

security = ClassSecurityInfo()

security.declarePublic('catalog_getcpsevents')
def catalog_getcpsevents(self, year, month):
    """ given a year and month return a list of days that have events """
    
    first_date=DateTime(str(month)+'/1/'+str(year))
    last_day=calendar.monthrange(year, month)[1]
    ## This line was cropping the last day of the month out of the
    ## calendar when doing the query
    ## last_date=DateTime(str(month)+'/'+str(last_day)+'/'+str(year))
    last_date=first_date + last_day    

    query = self.search(query={'portal_type':self.calendar_types,'review_state':'published'},start_date=first_date,end_date=last_date)

    # compile a list of the days that have events
    eventDays={}
    for daynumber in range(1, 32): # 1 to 31
        eventDays[daynumber] = {'eventslist':[], 'event':0, 'day':daynumber}
    for q in query:
        result = q.getContent()
        event={}
        # we need to deal with events that end next month
        if  result.end().month() != month:  # doesn't work for events that last ~12 months - fix it if it's a problem, otherwise ignore
            eventEndDay = last_day
            event['end'] = None
        else:
            eventEndDay = result.end().day()
            event['end'] = result.end().Time()
        # and events that started last month
        if result.start().month() != month:  # same as above re: 12 month thing
            eventStartDay = 1
            event['start'] = None
        else:
            eventStartDay = result.start().day()
            event['start'] = result.start().Time()
        event['title'] = result.Title or result.id
        if eventStartDay != eventEndDay:
            allEventDays = range(eventStartDay, eventEndDay+1)
            eventDays[eventStartDay]['eventslist'].append({'end':None, 'start':result.start().Time(), 'title':result.Title})
            eventDays[eventStartDay]['event'] = 1
            for eventday in allEventDays[1:-1]:
                eventDays[eventday]['eventslist'].append({'end':None, 'start':None, 'title':result.Title})
                eventDays[eventday]['event'] = 1
            eventDays[eventEndDay]['eventslist'].append({'end':result.end().Time(), 'start':None, 'title':result.Title})
            eventDays[eventEndDay]['event'] = 1
        else:
            eventDays[eventStartDay]['eventslist'].append(event)
            eventDays[eventStartDay]['event'] = 1
    return eventDays

security.declarePublic('getCPSEventsForCalendar')
def getCPSEventsForCalendar(self, month='1', year='2002'):
    """ recreates a sequence of weeks, by days each day is a mapping.
    {'day': #, 'url': None}
    """
    
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
    
    events=self.catalog_getcpsevents(year, month)
    
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
def getCPSEventsForThisDay(self, thisDay):
    """ given an exact day return ALL events that:
    A) Start on this day  OR
    B) End on this day  OR
    C) Start before this day  AND  end after this day"""

    query = self.search(query={'portal_type':self.calendar_types,'review_state':'published'},start_date=thisDay,end_date=thisDay)

    results = []

    for q in query:
        results.append(q)
                
    def sort_function(x,y):
        x_doc = x.getContent()
        y_doc = y.getContent()
        try:
            z = cmp(x_doc.start(),y_doc.start())
            if not z: 
                return cmp(x_doc.end(),y_doc.end())
            return z
        except AttributeError,ae:
            LOG('CMFCalendarToolPatch.getCPSEventsForThisDay: Error: missing attribute: ',DEBUG,ae)
            return 0
    
    # Sort by start date
    results.sort(sort_function)

    return results

#Adding methods to class CalendarTool
CalendarTool.CalendarTool.getCPSEventsForCalendar = getCPSEventsForCalendar
CalendarTool.CalendarTool.catalog_getcpsevents = catalog_getcpsevents
CalendarTool.CalendarTool.getCPSEventsForThisDay = getCPSEventsForThisDay

