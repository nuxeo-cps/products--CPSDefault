# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
# $Id$

# TODO: using this as a base class introduce a dependency for products
# (like CPSSchemas, CPSDdocument or CPSDirectory) that should be independent
# of CPS. So this module might go to its own product someday.

import os
from App.Extensions import getPath
from re import match
from zLOG import LOG, INFO, DEBUG

class BaseInstaller:
    """Base class for product-specific installers"""

    SECTIONS_ID = 'sections'
    WORKSPACES_ID = 'workspaces'

    def __init__(self, context):
        self._log = []
        self.context = context
        self.portal = context.portal_url.getPortalObject()
        self.workspaces = self.portal[self.WORKSPACES_ID]
        self.sections = self.portal[self.SECTIONS_ID]


    #
    # Logging
    #
    def log(self, bla, zlog=1):
        self._log.append(bla)
        if (bla and zlog):
            LOG('CPSDocument install:', INFO, bla)

    def logOK(self):
        self.log(" Already correctly installed")

    def logResult(self):
        return '<html><head><title>CPSDocument Update</title></head>' \
            '<body><pre>'+ '\n'.join(self._log) + '</pre></body></html>'

    #
    # These methods do the actual work
    #
    def setupSkins(self, skins):
        """Install or update skins.

        <skins> parameter is a sequence of (<skin_name>, <skin_path>)."""

        skin_installed = 0
        for skin, path in skins:
            path = path.replace('/', os.sep)
            self.log(" FS Directory View '%s'" % skin)
            if skin in self.portal.portal_skins.objectIds():
                dv = self.portal.portal_skins[skin]
                oldpath = dv.getDirPath()
                if oldpath == path:
                    self.logOK()
                else:
                    self.log("  Correctly installed, correcting path")
                    dv.manage_properties(dirpath=path)
            else:
                skin_installed = 1
                self.portal.portal_skins.manage_addProduct['CMFCore'].manage_addDirectoryView(filepath=path, id=skin)
                self.log("  Creating skin")

        if skin_installed:
            all_skins = self.portal.portal_skins.getSkinPaths()
            for skin_name, skin_path in all_skins:
                if skin_name != 'Basic':
                    continue
                path = [x.strip() for x in skin_path.split(',')]
                path = [x for x in path if x not in skins] # strip all
                if path and path[0] == 'custom':
                    path = path[:1] + [skin[0] for skin in skins] + path[1:]
                else:
                    path = [skin[0] for skin in skins] + path
                npath = ', '.join(path)
                self.portal.portal_skins.addSkinSelection(skin_name, npath)
                self.log(" Fixup of skin %s" % skin_name)
            self.log(" Resetting skin cache")
            self.portal._v_skindata = None
            self.portal.setupCurrentSkin()

    def setupTranslations(self):
        """Import .po files into the Localizer/default Message Catalog."""

        mcat = self.portal.Localizer.default
        self.log(" Checking available languages")
        podir = os.path.join('Products', self.product_name)
        popath = getPath(podir, 'i18n')
        if popath is None:
            self.log(" !!! Unable to find .po dir")
        else:
            self.log("  Checking installable languages")
            langs = []
            avail_langs = mcat.get_languages()
            self.log("    Available languages: %s" % str(avail_langs))
            for file in os.listdir(popath):
                if file.endswith('.po'):
                    m = match('^.*([a-z][a-z])\.po$', file)
                    if m is None:
                        self.log('    Skipping bad file %s' % file)
                        continue
                    lang = m.group(1)
                    if lang in avail_langs:
                        lang_po_path = os.path.join(popath, file)
                        lang_file = open(lang_po_path)
                        self.log("    Importing %s into '%s' locale" % (file, lang))
                        mcat.manage_import(lang, lang_file)
                    else:
                        self.log('    Skipping not installed locale for file %s' % file)

