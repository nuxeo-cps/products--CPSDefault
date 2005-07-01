## Script (Python) "wf_daf_soumettre_demande_after"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=Soumettre la demande
##
from Products.CMFCore.utils import getToolByName

# let the DAF tool method perform this action
# as a common user will not be authorized to do it...
proxy = state_change.object
daf_tool = getToolByName(proxy, 'portal_daf')
daf_tool.soumettreDemande(proxy)
