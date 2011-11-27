# (C) Copyright 2009 Association Paris-Montagne
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
# $Id: __init__.py 890 2008-06-18 18:26:32Z joe $

from Testing import ZopeTestCase

from Products.CPSDefault.tests.CPSTestCase import (
    CPSTestCase,
    ExtensionProfileLayerClass)

# register profiles
ZopeTestCase.installProduct('CPSDefault')

class CPSAdvancedDisplayLayerClass(ExtensionProfileLayerClass):
    extension_ids = ('CPSDefault:folder_advanced_display', )

CPSAdvancedDisplayLayer = CPSAdvancedDisplayLayerClass(
    __name__,
    'CPSAdvancedDisplayLayer'
    )

