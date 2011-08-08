# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: G. Racinet <gracinet@nuxeo.com>
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
"""Replays site factory's meta profiles"""

from Products.CPSDefault.jobs.replaymetaprofiles import replay as module_replay

def replay(self, REQUEST=None):

    steps = REQUEST.form.get('steps', ())
    excluded_steps = REQUEST.form.get('excluded_steps', ())
    log = module_replay(self, steps=steps, excluded_steps=excluded_steps)

    if REQUEST is not None:
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')
        return '\n'.join(log)
