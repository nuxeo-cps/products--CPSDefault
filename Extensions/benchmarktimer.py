# $Id$
# benchmarker from zopelabs'cookbook submited by zopedan
""" Benchmark tools are available if
 BENCHMARCKTIMER_LEVEL is defined in environment
"""

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityInfo import allow_class
from Acquisition import Implicit
import Globals
import time
import os

tidy_hook = """
<script type="text/javascript">
function setBodyContent() {
  document.tidyform.body_content.value = document.body.innerHTML;
  return true;
}
</script>
<form class="doNotPrint" name="tidyform" action="tidy" method="post"
  target="_blank" onsubmit="return setBodyContent()">
<input type="hidden" name="body_content" />
<input type="submit" value="Tidy the body of this page" />
</form>
"""

class pyBenchmarkTimer:
    def __init__(self, title='', level=-1):
        """
        Constructor, initializes
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
        """Are we benching or not """
        return self._in_bench

    def start(self):
        """
        Set the marker 'Start'
        a cheat shortcut function for basic use
        """
        return self.setMarker('Start')

    def stop(self):
        """
        Set the marker 'Stop'
        a cheat shortcut function for basic use
        """
        self.setMarker('Stop')

    def setMarker(self, name):
        """
        Set the specific marker
        """
        if not self._in_bench:
            return
        self.markers[name] = time.time()
        self.markerOrder.append(name)

    def timeElapsed(self, start=None, end=None):
        """
        Time diff between two markers, order is unimportant
            returns the absolute value of the difference
        If called without arguments, return the time
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
        str = '<pre class="doNotPrint">Profiling lvl:%d %s:\n' % (
            self._level, self.title)
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
                str += '%7.4f: %-10s +<span style="color:red">%7.4f</span>\n' % (
                       total, name, diff)
            else:
                str += '%7.4f: %-10s +%7.4f\n' % (total, name, diff)

            temp = time
            i = i+1
        str += '</pre>'
        str += tidy_hook

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

# HACK: this wasn't needed with Python 2.3 but it seems to be needed (at least
# for unit tests to pass) with Python 2.4.
allow_class(zBenchmarkTimer)

def BenchmarkTimerInstance(title='', level=-1):
    ob = zBenchmarkTimer(title, level)
    return ob
