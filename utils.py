# -*- coding: iso-8859-15 -*-
# (C) Copyright 2003-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
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
"""Miscellaneous utility functions.
"""

from Products.CMFDefault.utils import bodyfinder
from AccessControl import allow_type, allow_class
from AccessControl import ModuleSecurityInfo
from zLOG import LOG, INFO, DEBUG
import re

# Allowing the methods of this file to be imported in restricted code
ModuleSecurityInfo('Products.CPSDefault.utils').declarePublic('getHtmlBody')
ModuleSecurityInfo('Products.CPSDefault.utils').declarePublic('getNonArchivedVersionContextUrl')
ModuleSecurityInfo('Products.CPSDefault.utils').declarePublic('truncateText')

# Regexp of the form xxx<body>xxx</body>xxx.
# DOTALL: Make the "." special character match any character at all, including a
# newline; without this flag, "." will match anything except a newline.
html_body_regexp = re.compile('.*<body.*?>(.*)</body>.*',
                              re.DOTALL)

strip_attributes_regexp = re.compile('xml:lang=".*?"\s?',
                                     re.DOTALL)

# This regexp is for path of the following forms :
# /cps/workspaces/cores/myDoc/view
# /cps/workspaces/cores/myDoc/archivedRevision/1/view
# /cps/workspaces/cores/myDoc/archivedRevision/1/archivedRevision/2/view
archived_revision_url_regexp = re.compile('/archivedRevision/\d+')


def getHtmlBody(html_content):
    """
    getHtmlBody
    """
    # Substituting the <html><body>xxx</body></html> by xxx.
    # This has the effect of getting the content of the <body> tag of an HTML
    # document.
    #html_body = re.sub(html_body_regexp, r'\1', html_content)
    html_body = bodyfinder(html_content)
    html_body = re.sub(strip_attributes_regexp, '', html_body)

    return html_body


def getNonArchivedVersionContextUrl(content_url):
    """
    getNonArchivedVersionContextUrl
    """
    # Removing any matched '/archivedRevision/\d+' if present
    content_url = re.sub(archived_revision_url_regexp, '', content_url)

    return content_url


def truncateText(text, size=25):
    """Middle truncature."""
    if text is None or len(text) < size:
        return text
    mid_size = (size-3)/2
    return text[:mid_size] + '...' + text[-mid_size:]
