# benchmarker from zopelabs'cookbook submited by zopedan

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
import Globals
import time

class pyBenchmarkTimer:
    def __init__(self):
        """
        constructor, initializes
        """
        self.markers = {}
        self.markerOrder = []

    def start(self):
        """
        set the marker 'Start'
        a cheat shortcut function for basic use
        """
        self.setMarker('Start')

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
        self.markers[name] = time.clock()
        self.markerOrder.append(name)

    def timeElapsed(self, start=None, end=None ):
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
                end   = self.markerOrder[-1]
        return abs(self.markers[end]-self.markers[start])

    def getProfiling(self, return_str=1):
        """
        name  -> name of marker
        time  -> absolute time set in marker
        diff  -> difference between this marker and last marker
        total -> difference between this marker and first marker
        """
        i       = 0
        total   = 0
        profiling = []
        str = '<pre>Profiling:<small>\n'
        str += '%-6s  %-10s %-4s\n' % ('t', 'mark', 'delta t')
        for name in self.markerOrder:
            time = self.markers[name]
            if i==0:
                diff = 0
            else:
                diff  = time - temp
                total = total + diff
            profiling.append( { 'name'  : name,
                                'time'  : time,
                                'diff'  : diff,
                                'total' : total } )
            if diff > 0.3:
                str += '%.4f: %-10s +<font color="red">%.4f</font>\n' % (total, name, diff)
            else:
                str += '%.4f: %-10s +%.4f\n' % (total, name, diff)
            
            temp = time
            i = i+1
        str += '</small></pre>'
        if return_str:
            return str
        return profiling
        

class zBenchmarkTimer(Implicit, pyBenchmarkTimer):
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.declarePublic('start')
    security.declarePublic('stop')
    security.declarePublic('setMarker')
    security.declarePublic('timeElapsed')
    security.declarePublic('getProfiling')

Globals.InitializeClass(zBenchmarkTimer)

def BenchmarkTimerInstance():
    ob = zBenchmarkTimer()
    return ob
