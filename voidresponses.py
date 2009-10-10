# (C) Copyright 2009 Georges Racinet, Nuxeo SA
# Author: Georges Racinet <georges@racinet.fr>
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
# $Id: interfaces.py 53724 2009-07-04 12:29:21Z gracinet $

class DummyVoidResponseHandler:
    """Just there to avoid a miss in component lookup
    """

    def __init__(self, context, request):
        pass

    def respond(self, portal=None):
        pass

