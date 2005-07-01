##parameters=body_content=None
##$Id$
"""
Tidy a page
"""
from cgi import escape
try:
    from mx import Tidy
except ImportError:
    return "you need to install mx Tidy"

#get the output
if body_content is None:
    obj = context
    input = obj()
else:
    input = body_content

input_l = input.split('\n')

# tidy it
(errors, warnings, output, errordata) = Tidy.tidy(input,
                                                  drop_empty_paras=1,
                                                  indent_spaces=2,
                                                  indent='auto',
                                                  wrap=80,
                                                  wrap_attributes='yes',
                                                  ident='yes',
                                                  xml='yes',
                                                  char_encoding='latin1',
                                                  output_xhtml=1,
                                                  acces=3,
                                                  )

errordata_l = errordata.split('\n')
if body_content:
    description = """Warning only the body part of the page was
 checked !!!, lines number displayed will not match with the original html
 sources."""
    # we remove the first warning about missing title ...
    warnings -= 1
    errordata_l = errordata_l[1:]
else:
    description = 'All the page was checked'


# display result
html_header = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <title>Tidy result</title>
  <link rel="stylesheet" type="text/css" media="all"
        href="default.css"/>
</head>
<body>
<div class="document">
<div style="margin: 1em" id="content">
<div class="documentActions">
  <button onclick="window.close()">Close</button>
</div>
<h1>Tidying</h1>
<div class="description">%(description)s</div>
"""

html_footer = """
</div>
</div>
</body>
</html>
"""

html_ko = """<div style="font-size: 400%; text-align: center; background: red;">This page SUX</div>"""
html_ok = """<div style="font-size: 400%; text-align: center; background: green;">Such a nice page !!!</div>"""


def display_line(input_l, n, c=2):
    start = n - c
    stop = n + c
    if start < 0:
        start = 0
    if stop > len(input_l):
        stop = len(input_l)
    print '<pre>'
    for i in range(start, stop):
        print '%s: %s' % (i, escape(input_l[i]))
    print '</pre>'
    return printed

context.REQUEST.RESPONSE.setHeader('content-type', 'text/html')

print html_header % {'description': description}

print '<h2>results</h2>'



if not errors and not warnings:
    print html_ok
    return printed

print html_ko
print '<ul>'
print '<li>errors : %s</li>' % errors
print '<li>warning : %s</li>' % warnings
print '</ul>'
print '<h2>detail</h2>'
print '<ul>'
for err in errordata_l:
    if err:
        print '<li>%s</li>' % escape(err)
        line_idx = err.find('line ')
        col_idx = err.find('column')
        if line_idx>=0 and col_idx >=0:
            try:
                n = int(err[line_idx+5:col_idx-1])
            except:
                n = 0
            print display_line(input_l, n)

print '</ul>'
print '<h2>tidy output</h2>'
print '<pre>%s</pre>' % escape(output)
print html_footer

return printed
