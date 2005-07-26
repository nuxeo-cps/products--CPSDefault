##parameters=box_url=None, REQUEST=None
# $Id$
"""
Creates an ATOM feed from a Content Box content.
"""

import re
from cgi import escape

SUMMARY_MAX_LENGTH = 200

try:
    # XXX AT: see if box_url has to be changed to be correct in virtual hosting
    # environments
    box = context.restrictedTraverse(box_url)
except KeyError:
    return "ERROR: Box not found"

# get the items
ret = box.getContents(context)
items = ret[0]

atom_feed = r"""<?xml version="1.0" encoding="ISO-8859-15"?>
<?xml-stylesheet href="%(css_url)s" type="text/css"?>
<feed version="0.3" xmlns="http://purl.org/atom/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <title mode="escaped" type="text/html">%(feed_title)s</title>
  <tagline type="text/plain">%(feed_tagline)s</tagline>
  <link rel="alternate" type="text/html" href="%(feed_link)s" />
  <id>%(feed_id)s</id>
  <generator url="%(generator_url)s" version="%(generator_version)s">CPS</generator>
  <modified>%(feed_modified)s</modified>
  %(entries)s
</feed>
"""
# " <- for Emacs Python mode, argh


atom_entry = r"""
  <entry>
    <title mode="escaped" type="text/html">%(entry_title)s</title>
    <id>%(entry_id)s</id>
    <link rel="alternate" type="text/html" href="%(entry_link)s" />
    <issued>%(entry_issued)s</issued>
    <modified>%(entry_modified)s</modified>
    <author>
      <name>%(entry_author)s</name>
    </author>
    %(entry_contributors)s
    <summary xml:lang="%(entry_lang)s">
      %(summary)s
    </summary>
  </entry>
"""

entry_contributor =r"""<contributor>
      <name>%(contributor)s</name>
    </contributor>
"""

def construct_id(permalink, datetime):
    """<link rel="alternate"> is always the permalink of the entry
    http://diveintomark.org/archives/2004/05/28/howto-atom-id - article
    about constructing id
    """
    urlregexp = r"^(http://|https://)([^/:]+):?(\d+)?(/.*)?$"
    m = re.search(urlregexp, permalink)
    if m:
        location, port, path = m.groups()[1:]
        uid = 'tag:' + location + ',' + datetime.strftime('%Y-%m-%d') + ':' + path
        return uid
    # problems parsing url, so permalink will be id
    return permalink

base_url = context.portal_url()+'/'

body_text = ''
for item in items:
    info = context.getContentInfo(item, level=1)
    doc = info['doc']
    entry_title = info.get('title', '')
    entry_link = info.get('url')
    # XXX: issued == doc.created()? or issued it's time when it was published?
    entry_issued = context.getDateStr(doc.created(), fmt='iso8601_long')
    entry_modified = context.getDateStr(info.get('time'), fmt='iso8601_long')
    entry_author = info.get('creator')
    entry_lang = info.get('language')
    entry_id = construct_id(entry_link, doc.created())

    entry_contributors = ''
    for contributor in doc.Contributors():
        entry_contributors += entry_contributor % {'contributor' : contributor}

    def strip_html(text):
        # stripping of html tags based on simple regexp
        return re.sub("<[^>]+>", '', text)

    if len(doc.Description()) > 0:
        summary = strip_html(doc.Description())
    else:
        summary = ''

    body_text += atom_entry % {'entry_id' : entry_id,
                               'entry_title' : escape(entry_title),
                               'entry_link' : entry_link,
                               'entry_issued' : entry_issued,
                               'entry_modified' : entry_modified,
                               'entry_author' : entry_author,
                               'entry_lang' : entry_lang,
                               'entry_contributors' : entry_contributors,
                               'summary' : summary
                               }

info = context.getContentInfo(context, level=1)
feed_title = info.get('title', '')
feed_link = info.get('url')
feed_id = construct_id(feed_link, context.created())
feed_modified = context.getDateStr(context.created(), fmt='iso8601_long')
generator_url = 'http://nuxeo.com'
try:
    generator_version = '.'.join([str(v) for v in context.cps_version[1:]])
except AttributeError:
    generator_version = 'unknown'

text = atom_feed % {'css_url': base_url + 'atom.css',
                    'feed_title' : escape(feed_title),
                    'feed_tagline' : 'ATOM feed',
                    'feed_link' : feed_link,
                    'feed_id' : feed_id,
                    'generator_url' : generator_url,
                    'generator_version' : generator_version,
                    'feed_modified' : feed_modified,
                    'entries' : body_text
                    }

if REQUEST is not None:
   REQUEST.RESPONSE.setHeader('Content-Type', 'application/xml; charset=ISO-8859-15')
   # FIXME: Why no-cache here ? We need something more sensible since
   # syndication generates lots of traffic.
   REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')

return text
