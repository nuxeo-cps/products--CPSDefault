"""
get all sections info with allowed publishing transitions
"""

sections = context.portal_trees.sections.getList(filter=0)

wftool = context.portal_workflow
allowed_transitions = wftool.getAllowedPublishingTransitions(context)
type_name = context.portal_type


for section in sections:
    transitions =  wftool.getInitialTransitions(section['rpath'], type_name,
                                                wftool.TRANSITION_INITIAL_PUBLISHING)
    transitions = [t for t in transitions if t in allowed_transitions]
    section['publishing_transitions'] = transitions

return sections
