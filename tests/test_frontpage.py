# (C) Copyright 2008 Association Paris-Montagne
# Author: Georges Racinet <georges.racinet@paris-montagne.org>
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

# testing harness
import unittest
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from advanceddisplaylayer import CPSAdvancedDisplayLayer

# other imports
from Products.CPSSchemas.DataStructure import DataStructure

class FrontPageTestCase(CPSTestCase):

    layer = CPSAdvancedDisplayLayer

    def afterSetUp(self):
        ws = self.workspaces = self.portal.workspaces
        wftool = self.wftool = self.portal.portal_workflow
        self.login('manager')
        wftool.invokeFactoryFor(ws, 'Workspace', 'folder')
        self.folder = ws.folder

    def test_front_page_select_widget(self):
        folder = self.folder
        layout = self.portal.portal_layouts.folder_display_options
        widget = layout['frontpage']
        dm = folder.getContent().getDataModel(proxy=folder)
        ds = DataStructure(datamodel=dm)

        def get_voc_keys():
            return widget._getVocabulary(datastructure=ds).keys()

        # testing first with an empty folder
        widget.prepare(ds)
        self.assertEquals(get_voc_keys(), [''])

        # now with a subfolder but still no candidate.
        wftool = self.wftool
        subf_id = wftool.invokeFactoryFor(folder, 'Workspace', 'subfolder')
        widget.prepare(ds)
        self.assertEquals(get_voc_keys(), [''])

        # now with a document
        wftool.invokeFactoryFor(folder, 'News Item', 'candidate')
        wftool.invokeFactoryFor(folder[subf_id], 'News Item', 'too_deep')
        widget.prepare(ds)
        self.assertEquals(get_voc_keys(), ['', 'candidate'])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FrontPageTestCase),
        ))

