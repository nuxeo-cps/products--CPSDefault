##parameters=
# $Id$
"""
Get all sections info with allowed publishing transitions
"""

sections = context.portal_trees.sections.getList()

wftool = context.portal_workflow
getInitialTransitions = wftool.getInitialTransitions
TRANSITION_INITIAL_PUBLISHING = wftool.TRANSITION_INITIAL_PUBLISHING
allowed_transitions = wftool.getAllowedPublishingTransitions(context)

type_name = context.portal_type
allowed_container_types = context.getAllowedContainerTypes(type_name)

res = []

for section in sections:
    if allowed_container_types is not None and not (
            section['portal_type'] in allowed_container_types):
        continue
    transitions = getInitialTransitions(section['rpath'], type_name,
                                        TRANSITION_INITIAL_PUBLISHING)
    transitions = [t for t in transitions if t in allowed_transitions]
    section['publishing_transitions'] = transitions
    res.append(section)

return res
