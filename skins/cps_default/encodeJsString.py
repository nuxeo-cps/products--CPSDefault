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

return jsstr
