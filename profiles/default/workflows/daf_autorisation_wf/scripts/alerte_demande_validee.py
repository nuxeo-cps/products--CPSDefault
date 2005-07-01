## Script (Python) "alerte_demande_validee"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=Alerter le checheur que la demande est validée
##
from Products.CMFCore.utils import getToolByName

proxy = state_change.object
evtool = getToolByName(proxy, 'portal_eventservice')
evtool.notifyEvent('alerte_demande_validee', proxy, {})
