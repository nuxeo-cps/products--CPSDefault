##parameters=key=None
#$Id$
"""Return a list of review state, used as MethodVocabulary."""

names = context.getWorkflowStateNames()
l10n = context.translation_service
res = [(name, l10n(name, default=name).capitalize()) for name in names]
res.insert(0, ('', l10n('label_all')))
if key is not None:
    res = [item[1] for item in res if item[0] == key][0]

return res
