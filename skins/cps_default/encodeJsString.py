##parameters=pystr=None
# $Id$
"""
Encode a python string into a javascript string

This is very usefull to set js variable like
 <script type="text/javascript"
  tal:define="js_value python:here.encodeJsString(value)"
  tal:content='structure string:
  <!--
      var value = "${js_value}";
  //--> />
"""
if not pystr:
    return ''

quotes = (("\\", "\\\\"),
          ("\n", "\\n"),
          ("\r", "\\r"),
          ("'", "\\'"),
          ('"', '\\"'))

jsstr = pystr
for item in quotes:
    jsstr = jsstr.replace(item[0], item[1])

if not isinstance(jsstr, unicode):
    # fckeditor return utf-8 encoded str
    jsstr = unicode(jsstr, 'utf-8')

return jsstr
