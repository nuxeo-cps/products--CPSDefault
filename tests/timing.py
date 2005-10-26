# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
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
# $Id: wikiversionning.py 28619 2005-10-25 15:17:14Z tziade $
"""
    absolute timer based on pystone measurement,
    this can be used to bench some code
    and get a absolute scoring

    example of usage:
    >>> import timing
    >>> timing.local_stones
    (1.23, 40650.406504065038)
    >>> def o():
    ...     a = ''
    ...     for i in range(50000):
    ...         a = '3' * 10
    ...     return a
    ...
    >>> o()
    '3333333333'
    >>> timing.pystoneit(o)
    2171.3598996304308

    The result can be used in unit test to make assertions
    and prevent performance regressions:

    >>> if timing.pystoneit(o) > 3*timing.kPS:
    ...   raise AssertionError('too slow !')
    ...
    >>> if timing.pystoneit(o) > 2*timing.kPS:
    ...   raise AssertionError('too slow !')
    ...
    Traceback (most recent call last):
    File "<stdin>", line 2, in ?
    AssertionError: too slow !

    Raising an assertion error in Unit tests
    leads to a regular test failure (F)

"""
from test import pystone
import time

# TOLERANCE in Pystones
kPS = 1000
TOLERANCE = 0.5*kPS

local_stones = local_pystone()

def pystoneit(function, *args, **kw):
    start_time = time.time()
    try:
        function(*args, **kw)
    finally:
        total_time = time.time() - start_time
        if total_time == 0:
            pystone_total_time = 0
        else:
            pystone_rate = local_stones[0] / local_stones[1]
            pystone_total_time = total_time / pystone_rate
    return pystone_total_time
