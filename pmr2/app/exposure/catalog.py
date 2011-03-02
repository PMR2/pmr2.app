import zope.interface
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName

from pmr2.app.converter import curation_to_textline_list
from pmr2.app.interfaces import IExposureSourceAdapter, IPMR2KeywordProvider
from pmr2.app.exposure.interfaces import *


# Apply to all exposure objects

@indexer(IExposureObject)
def pmr2_review_state(self):
    # provide the intended review state that PMR2 uses.
    helper = zope.component.queryAdapter(self, IExposureSourceAdapter)
    exposure = helper.exposure()
    wf = getToolByName(exposure, 'portal_workflow')
    return wf.getInfoFor(exposure, 'review_state', '')


# Apply to the root exposure object only

@indexer(IExposure)
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

@indexer(IExposure)
def pmr2_exposure_workspace(self):
    return self.workspace

@indexer(IExposure)
def pmr2_exposure_commit_id(self):
    return self.commit_id

@indexer(IExposure)
def pmr2_exposure_root_title(self):
    return self.Title()

@indexer(IExposure)
def pmr2_exposure_root_path(self):
    return self.absolute_url_path()

@indexer(IExposure)
def pmr2_exposure_root_id(self):
    return self.id

# Apply to exposure files only

@indexer(IExposureFile)
def pmr2_keyword(self):
    kw_providers = zope.component.getUtilitiesFor(IPMR2KeywordProvider)
    results = []
    for name, provider in kw_providers:
        # it may be better to handle exceptions which may be triggered
        # by the provider and turn that into a warning message with 
        # a partial stack trace.
        results.extend(provider(self))
    return results

# ExposureFileType

@indexer(IExposureFileType)
def pmr2_eftype_views(self):
    return self.views

@indexer(IExposureFileType)
def pmr2_eftype_select_view(self):
    return self.select_view

@indexer(IExposureFileType)
def pmr2_eftype_tags(self):
    return self.tags
