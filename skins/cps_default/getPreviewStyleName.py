##parameters=subfiles_name=''
# $Id$
"""
Checks if a preview_html.css is present
build the <link> tag and returns it
returns empty string if none available

<link rel="Stylesheet" type="text/css" media="all" href="preview_html.css" />
"""
link_tag=''

if subfiles_name != '':
    content = context.getContent()
    try:
        subfiles = content[subfiles_name]
    except KeyError:
        return ''

    for afile in subfiles:
        if afile.endswith('.css'):
            link_tag += '<link rel="Stylesheet" type="text/css" media="all" href="%s" />' %(str(afile))

return link_tag
