##parameters=item=None, brain=None, dodateiso=0, modify_brain_url=1

# This script must deal with real objects and with brains

if item is None and brain is None:
    item = context.this()

if item is not None:
    wftool = context.portal_workflow

    id = item.getId()
    url = item.absolute_url()
    folderish = getattr(item, 'isPrincipiaFolderish', 0)
    contentish = getattr(item, 'isPortalContent', 0)

    try:
        ricon = item.getIcon(relative_to_portal=1)
    except AttributeError:
        ricon = ''
    if not ricon:
        ricon = getattr(item, 'icon', '')
        if callable(ricon):
            ricon = ricon()

    try: typ = item.Type()
    except AttributeError: typ = ''

    try: portal_typ = item.portal_type
    except AttributeError: portal_typ = ''

    try:
        title = item.Title()
    except AttributeError:
        title = ''

    try: description = item.Description()
    except AttributeError: description = ''

    try: moddate = item.ModificationDate()
    except AttributeError: moddate = None

    try: creadate = item.CreationDate()
    except AttributeError: creadate = None

    try: isdocumentcontainer = item.isDocumentContainer
    except: isdocumentcontainer = 0

    review_state = wftool.getInfoFor(item, 'review_state', None)

    if dodateiso: # for explicit date in item
        dateiso = item.dateiso

else:
    # XXX Probably buggy and untested
    id = brain.id
    url = brain.getURL()
    folderish = brain.isPrincipiaFolderish
    contentish = brain.isPortalContent
    isdocumentcontainer = 0 # XXX fix me
    ricon = brain.getIconRelative # relative to portal
    typ = brain.Type
    portal_typ = brain.portal_type
    title = brain.Title
    description = brain.Description
    creadate = brain.CreationDate
    moddate = brain.ModificationDate

    review_state = brain.review_state
    if dodateiso: # for explicit date in item
        dateiso = brain.dateiso


action = contentish and 'view' or (folderish and 
(isdocumentcontainer and 'workgroup_contents' or 'folder_contents') or '')
date_format = '%m/%d/%Y %H:%M'
if title:
    thetitle = title
else:
    thetitle = id
if moddate:
    modification = DateTime(moddate).strftime(date_format)
else:
    moddate = ''
    modification = ''

if creadate:
    creation = DateTime(creadate).strftime(date_format)
else:
    creadate = ''
    creation = ''

portal_url = context.portal_url(relative=1)
if portal_url: portal_url = '/'+portal_url
if ricon:
    icon = portal_url + '/' + ricon
else:
    icon = ''

d = {
     'item': item,
     'brain': brain,
     'id': id,
     'isup': 0, # caller should change this if needed
     'url': url,
     'icon': icon,
     'action': action,
     'type': typ,
     'portal_type': portal_typ,
     'folderish': not not folderish,
     'contentish': not not contentish,
     'title': thetitle,
     'description': description,
     'creadate': creadate,
     'creation': creation,
     'moddate': moddate,
     'modification': modification,
     'review_state': review_state,
     # 'for cmf compatibility'
     'isPrincipiaFolderish': not not folderish,
     'isPortalContent': not not contentish,
     'getId': id,
     'Title': thetitle,
}

if dodateiso:
    d['dateiso'] = dateiso

return d
