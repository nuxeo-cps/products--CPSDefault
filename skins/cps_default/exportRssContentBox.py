##parameters=box_url=None, REQUEST=None
# $Id$
"""
Create a rss 1.0 feed from a Content Box content
"""

from cgi import escape

try:
    # XXX AT: see if box_url has to be changed to be correct in virtual hosting
    # environments
    box = context.restrictedTraverse(box_url)
except KeyError:
    return "ERROR: Box not found"

# get the items
ret = box.getContents(context)
items = ret[0]

# this is the hard coded rss 1.0
rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

rss_fmt = r"""<?xml version="1.0" encoding="ISO-8859-15"?>
<?xml-stylesheet href="%(css_url)s" type="text/css"?>
<rdf:RDF
  xmlns:rdf="%(rdf_ns)s"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns="http://purl.org/rss/1.0/"
  xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <channel rdf:about="%(channel_about)s">
    <title>%(channel_title)s</title>
    <description>%(channel_description)s</description>
    <link>%(channel_link)s</link>

    <items>
      <rdf:Seq>
%(items_li)s
      </rdf:Seq>
    </items>

  </channel>


%(items)s

  <xhtml:script id="js" type="text/javascript" src="%(js_url)s" />

</rdf:RDF>
"""

rss_item_li = """        <rdf:li rdf:resource="%(item_id)s" />\n"""

rss_item = """  <item rdf:about="%(item_id)s">
    <title>%(item_title)s</title>
    <description>%(item_description)s</description>
    <link>%(item_link)s</link>
%(item_dc)s
  </item>\n"""

rss_item_dc = """    <dc:%(dc_key)s>%(dc_value)s</dc:%(dc_key)s>\n"""

# dublin core available from getContentInfo
dc_keys = ('subject', 'date', 'creator',
           'contributor', 'rights', 'language',
           'coverage', 'relation', 'source')

# computed value
base_url = context.portal_url()+'/'
channel_url = context.absolute_url() + '/exportRssContentBox?' + \
              context.REQUEST.environ.get('QUERY_STRING')
channel_description = "RSS 1.0 export of the CPS Box named '%s' from the folder '%s'." % (
    box.title_or_id(), context.title_or_id())

header_text = body_text = ''
for item in items:
    info = context.getContentInfo(item, level=1)
    url = info.get('url')
    header_text += rss_item_li % {'item_id': url}
    item_date = context.getDateStr(info.get('time'), fmt='iso8601')
    dc_text = ''
    for key in dc_keys:
        if key == 'date':
            value = item_date
        else:
            value = info.get(key)
        if value:
            dc_text += rss_item_dc % {'dc_key': key,
                                      'dc_value': escape(value)}
    body_text += rss_item % {'item_id': url,
                             'item_title': escape(info.get('title', '')),
                             'item_description': escape(info.get('description',
                                                                 '')),
                             'item_link': url,
                             'item_dc': dc_text,}

text = rss_fmt % {'css_url': base_url + 'rss.css',
                  'rdf_ns': rdf_ns,
                  'channel_about': channel_url,
                  'channel_title': escape(box.title_or_id()),
                  'channel_link': channel_url,
                  'channel_description': escape(channel_description),
                  'items_li': header_text,
                  'items': body_text,
                  'js_url': base_url + 'rss.js',
                  }

if REQUEST is not None:
   REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml; charset=ISO-8859-15')
   # FIXME: why no-cache ?
   REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')

return text
