##parameters=actions=None

if not actions:
    actions=context.portal_actions.listFilteredActionsFor(context);

actionsblocks = filter(None, [actions['workflow'],
                              actions['object'],
                              actions['folder'],
                             ])
return actionsblocks
