from zope.component import getAdapter
from zope.component import queryAdapter

from plone.app.portlets.portlets import base

from Acquisition import aq_inner, aq_parent
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from pmr2.app.interfaces.exceptions import WorkspaceObjNotFoundError

from pmr2.app.exposure.interfaces import *
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile


class BaseRenderer(base.Renderer):

    _error_template = ViewPageTemplateFile('exposure_fallback_portlet.pt')

    def __init__(self, *a, **kw):
        base.Renderer.__init__(self, *a, **kw)

        # base availability solely on whether context is IExposureObject
        # subclasses can deal with further constraints by exp
        if BaseRenderer._available(self):
            # If these were called/initialized in the update method,
            # it seems like they will somehow be implicitly wrapped by
            # Acquisition and that causes unwanted effects, like
            # absolute_url not working.
            try:
                self.exposure, self.workspace, self.path = getAdapter(
                    self.context, IExposureSourceAdapter).source()
            except WorkspaceObjNotFoundError:
                # Yes people have deleted workspaces, somehow...
                self.exposure = self.workspace = self.path = None
                return
            # further init.
            self.exposure_source_init()

    def exposure_source_init(self):
        # For further assignment of initial values, if it worked.
        pass

    @property
    def available(self):
        return self._available()

    def _available(self):
        return IExposureObject.providedBy(self.context)

    def render(self):
        try:
            return self._template()
        except AttributeError:
            return self._error_template()
