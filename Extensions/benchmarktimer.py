# $Id$
# benchmarker from zopelabs'cookbook submited by zopedan
""" Benchmark tools are available if
 BENCHMARCKTIMER_LEVEL is define in environment
"""

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
import Globals
import time
import os

class pyBenchmarkTimer:
    def __init__(self, title='', level=-1):
        """
        constructor, initializes
        """
        self.title = title
        self.markers = {}
        self.markerOrder = []
        self._level = level
        self._level_display = int(os.environ.get('BENCHMARKTIMER_LEVEL', 0))
        if self._level_display and (self._level >= self._level_display):
            self._in_bench = 1
        else:
            self._in_bench = 0

    def in_bench(self):
        """ are we benching or not """
        return self._in_bench

    def start(self):
        """
        set the marker 'Start'
        a cheat shortcut function for basic use
        """
        return self.setMarker('Start')

    def stop(self):
        """
        set the marker 'Stop'
        a cheat shortcut function for basic use
        """
        self.setMarker('Stop')

    def setMarker(self,name):
        """
        set the specific marker
        """
        if not self._in_bench:
            return
        self.markers[name] = time.clock()
        self.markerOrder.append(name)

    def timeElapsed(self, start=None, end=None):
        """
        time diff between two markers, order is unimportant
            returns the absolute value of the difference
        if called without arguments, return the time
            elapsed from the first marker to the last marker
        """
        if len(self.markerOrder) < 2:
            return 0
        if start is None:
            start = self.markerOrder[0]
        if end is None:
            end = self.markerOrder[-1]
        return abs(self.markers[end] - self.markers[start])

    def getProfiling(self, return_str=1):
        """
        name  -> name of marker
        time  -> absolute time set in marker
        diff  -> difference between this marker and last marker
        total -> difference between this marker and first marker
        """
        if not self._in_bench:
            return
        i = 0
        total = 0
        profiling = []
        str = '<pre>Profiling lvl:%d %s:<small>\n' % (self._level, self.title)
        str += '%-6s  %-10s %-4s\n' % ('t', 'mark', 'delta t')
        for name in self.markerOrder:
            time = self.markers[name]
            if i == 0:
                diff = 0
            else:
                diff = time - temp
                total = total + diff
            profiling.append({'name'  : name,
                              'time'  : time,
                              'diff'  : diff,
                              'total' : total})
            if diff > 0.3:
                str += '%7.4f: %-10s +<font color="red">%7.4f</font>\n' % (
                       total, name, diff)
            else:
                str += '%7.4f: %-10s +%7.4f\n' % (total, name, diff)
            
            temp = time
            i = i+1
        str += '</small></pre>'
        
        if return_str:
            return str
        return profiling

    def saveProfile(self, REQUEST):
        if not self._in_bench:
            return
        str = REQUEST.other.get('bench_mark_profiler', '')
        REQUEST.other['bench_mark_profiler'] = str + self.getProfiling()


class zBenchmarkTimer(Implicit, pyBenchmarkTimer):
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.declarePublic('start')
    security.declarePublic('stop')
    security.declarePublic('setMarker')
    security.declarePublic('timeElapsed')
    security.declarePublic('getProfiling')
    security.declarePublic('saveProfile')
    security.declarePublic('in_bench')

Globals.InitializeClass(zBenchmarkTimer)

def BenchmarkTimerInstance(title='', level=-1):
    ob = zBenchmarkTimer(title, level)
    return ob
