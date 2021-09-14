from zope import schema
from zope.formlib import form
from zope.interface import implements
import zope.component

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey
from plone.memoize.view import memoize

from Acquisition import aq_inner, aq_parent
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from pmr2.app.exposure.interfaces import IExposureObject
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.workspace.interfaces import IStorageUtility
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile

from pmr2.app.exposure.portlets.base import BaseRenderer


class ICollaborationPortlet(IPortletDataProvider):
    """\
    Exposure Information portlet.
    """


class Assignment(base.Assignment):
    implements(ICollaborationPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Exposure Collaboration Info")


class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('exposure_collab.pt')

    def exposure_source_init(self):
        utility = zope.component.queryUtility(IStorageUtility,
            name=self.workspace.storage)
        self.command = getattr(utility, 'command', self.workspace.storage)
        self.clone_verb = getattr(utility, 'clone_verb', 'clone')

    @memoize
    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    @memoize
    def repotype(self):
        return self.workspace.storage

    @memoize
    def clonecmd(self):
        exposure, workspace, path = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter).source()
        storage = IStorage(workspace)
        storage.checkout(exposure.commit_id)
        cmd = storage.clonecmd()
        if cmd:
            # TODO, if None, it may in fact mean this workspace is
            # uncloneable.
            return cmd

        # previous inferred implementation based on utility
        workspace_uri = self.workspace.absolute_url()
        # TODO formalize on how this is derived
        result = '%s %s %s' % (
            self.command,
            self.clone_verb,
            self.workspace.absolute_url(),
        )
        return result


class AddForm(base.AddForm):
    form_fields = form.Fields(ICollaborationPortlet)
    label = _(u"Add Exposure Collaboration Info Portlet")
    description = _(
        u"This portlet displays information as to how to collaborate with the "
        "workspace protocol.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(ICollaborationPortlet)
    label = _(u"Edit Exposure Collaboration Info Portlet")
    description = (
        u"This portlet displays information as to how to collaborate with the "
        "workspace protocol.")
