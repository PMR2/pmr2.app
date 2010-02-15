import zope.interface
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName

from pmr2.app.converter import curation_to_textline_list
from pmr2.app.content.interfaces import *

@indexer(IExposureObject)
def pmr2_review_state(self):
    # provide the intended review state that PMR2 uses.
    wf = getToolByName(self, 'portal_workflow')
    return wf.getInfoFor(self, 'review_state', '')

@indexer(IExposureObject)
def pmr2_curation(self):
    """
    This processes the key/values dictionary that represents curation
    into a list of friendlier values.
    """

    if not self.curation:
        return []
    value = self.curation
    # index the keys first
    result = self.curation.keys()
    # then the values
    result.extend(curation_to_textline_list(value))
    return result

@indexer(IExposureObject)
def pmr2_exposure_workspace(self):
    return self.workspace
