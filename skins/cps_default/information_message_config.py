##parameters=REQUEST=None
"""Returns the rendered form and does the config setting on submit."""

from logging import getLogger
logger = getLogger('information_message_config')

portal = context.portal_url.getPortalObject()

res = {'rendered_form': '',
       'status': '',
       'psm': '',
       'valid_form': 0,
       }

if REQUEST is not None:
    form = REQUEST.form
    # This is a form submission
    if form.has_key('information_message_config_submit'):
        mapping = form
    else:
        mapping = None
else:
    mapping = None

ltool = portal.portal_layouts
infotool = portal.portal_information_message
config = {}
config_items = infotool.propertyItems()
for k, v in config_items:
    config[k] = v
//logger.debug("Read config: %s" % config)

(res['rendered_form'], res['status'], ds) = ltool.renderLayout(
    layout_id='information_message', schema_id='information_message',
    context=context, mapping=mapping, ob=config)

if mapping is not None:
    if res['status'] == 'valid':
        infotool.config(config)
        res['valid_form'] = True
    else:
        res['psm'] = 'psm_content_error'

return res
