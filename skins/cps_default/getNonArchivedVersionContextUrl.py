##parameters=content_url
# $Id$
"""Removes the reference to an archived version if there is one present.
"""

import re

# This regexp is for path of the following forms :
# /cps/workspaces/cores/myDoc/view
# /cps/workspaces/cores/myDoc/archivedRevision/1/view
# /cps/workspaces/cores/myDoc/archivedRevision/1/archivedRevision/2/view
#
# Removing any matched '/archivedRevision/\d+' if present
contentUrl = re.sub('/archivedRevision/\d+', '', content_url)

return contentUrl

