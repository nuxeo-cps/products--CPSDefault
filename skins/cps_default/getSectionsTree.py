##parameters=
# $Id$
"""Get all sections info with allowed publishing transitions"""

sections = context.portal_trees.sections.getList()

wftool = context.portal_workflow
allowed_transitions = wftool.getAllowedPublishingTransitions(context)
type_name = context.portal_type

res = []

allowed_container_types = context.getAllowedContainerTypes(type_name)

if allowed_container_types:
    for section in sections:
        if section['portal_type'] in allowed_container_types:
            transitions = wftool.getInitialTransitions(section['rpath'], 
                 type_name, wftool.TRANSITION_INITIAL_PUBLISHING)
            transitions = [t for t in transitions if t in allowed_transitions]
            section['publishing_transitions'] = transitions
            res.append(section)
else:
    for section in sections:
        transitions =  wftool.getInitialTransitions(section['rpath'],
            type_name, wftool.TRANSITION_INITIAL_PUBLISHING)
        transitions = [t for t in transitions if t in allowed_transitions]
        section['publishing_transitions'] = transitions
        res.append(section)
        
return res
