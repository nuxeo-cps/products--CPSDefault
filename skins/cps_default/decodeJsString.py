##parameters=jsstr=None
# $Id$
"""
Decode a javascript string into a python string
"""

pystr = jsstr
if not pystr:
    return ''

# Quote newlines and single quotes, so JavaScript won't break.
quotes = (("\\\\r", "\\r"),
          ("\\\\n", "\\n"),
          ("\\'", "'"),
          ("\\r", "\r"),
          ("\\n", "\n"),
          ("\\\\", "\\"))

for item in quotes:
    pystr = pystr.replace(item[0], item[1])

return pystr
