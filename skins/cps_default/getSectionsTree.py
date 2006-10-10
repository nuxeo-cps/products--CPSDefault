##parameters=root_id=None
# $Id$
"""
Get all sections info with allowed publishing transitions

You can specify root_id if the sections are located elsewhere
"""

if root_id is not None:
    sections_roots = [root_id]
else:
    sections_roots = context.getSectionsRoots()

locale = context.translation_service.getSelectedLanguage()
ptree = context.portal_trees
available_roots = ptree.objectIds()

sections = []
for root_uid in sections_roots:
    if not root_uid in available_roots:
        continue
    sections.extend(ptree[root_uid].getList(
        locale_keys=('title', 'short_title'),
        locale_lang=locale))

wftool = context.portal_workflow
getInitialTransitions = wftool.getInitialTransitions
isBehaviorAllowedFor = wftool.isBehaviorAllowedFor
TRANSITION_INITIAL_PUBLISHING = wftool.TRANSITION_INITIAL_PUBLISHING
allowed_transitions = wftool.getAllowedPublishingTransitions(context)

type_name = context.portal_type
allowed_container_types = context.getAllowedContainerTypes(type_name)

res = []

for section in sections:
    if allowed_container_types is not None and not (
            section['portal_type'] in allowed_container_types):
        continue
    if not isBehaviorAllowedFor(section['rpath'], 'publishing'):
        continue
    transitions = getInitialTransitions(section['rpath'], type_name,
                                        TRANSITION_INITIAL_PUBLISHING)
    transitions = [t for t in transitions if t in allowed_transitions]
    section['publishing_transitions'] = transitions
    res.append(section)

return res
