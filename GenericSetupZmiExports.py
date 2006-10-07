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
# $Id$

"""Enable Generic Setup ZMI XML Export for a few objects.

Done by monkey patching to avoid creating dependencies upon CPSUtil
"""
from Products.CPSUtil import export_option

# Theme Tool
from Products.CPSSkins.PortalThemesTool import PortalThemesTool
PortalThemesTool.manage_options += export_option

# Action Icons Tool
# Uncomment when this tool's export is done the adapter way

#from Products.CMFActionIcons.ActionIconsTool import ActionIconsTool
#ActionIconsTool.manage_options += export_option

# Actions Tool
from Products.CMFCore.ActionsTool import ActionsTool
ActionsTool.manage_options += export_option
