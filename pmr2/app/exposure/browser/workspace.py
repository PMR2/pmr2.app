import json

import zope.component
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest

import z3c.form
from plone.z3cform import layout
from plone.z3cform.fieldsets import group, extensible

from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage

from pmr2.app.workspace.interfaces import IStorage, IWorkspace
from pmr2.app.workspace.exceptions import *

from pmr2.app.interfaces import *
from pmr2.app.interfaces.exceptions import *
from pmr2.app.browser.interfaces import *
from pmr2.app.annotation.interfaces import *
from pmr2.app.exposure.content import *

from pmr2.app.browser import form
from pmr2.app.browser import page
from pmr2.app.browser import widget
from pmr2.app.browser.layout import *

from pmr2.app.exposure.interfaces import *
from pmr2.app.exposure.browser.interfaces import *
from pmr2.app.exposure.browser.util import *
from pmr2.app.exposure.urlopen import urlopen


class ExtensibleAddForm(form.AddForm, extensible.ExtensibleForm):

    def __init__(self, *a, **kw):
        super(ExtensibleAddForm, self).__init__(*a, **kw)
        self.groups = []
        self.fields = z3c.form.field.Fields()

    def update(self):
        extensible.ExtensibleForm.update(self)
        form.AddForm.update(self)


class CreateExposureForm(ExtensibleAddForm, page.TraversePage):
    """\
    Page that will create an exposure inside the default exposure
    container from within a workspace.
    """

    _gotExposureContainer = False

    def create(self, data):
        # no data assignments here
        self._data = data
        generator = getGenerator(self)
        eid = generator.next()
        return Exposure(eid)

    def add(self, obj):
        """\
        The generic add method.
        """
        if not self.traverse_subpath:
            raise NotFound(self.context, self.context.title_or_id())

        exposure = obj
        workspace = u'/'.join(self.context.getPhysicalPath())
        commit_id = unicode(self.traverse_subpath[0])

        try:
            exposure_container = restrictedGetExposureContainer()
        except Unauthorized:
            self.status = 'Unauthorized to create new exposure.'
            raise z3c.form.interfaces.ActionExecutionError(
                ExposureContainerInaccessibleError())
        self._gotExposureContainer = True

        exposure_container[exposure.id] = exposure
        exposure = exposure_container[exposure.id]
        exposure.workspace = workspace
        exposure.commit_id = commit_id
        exposure.setTitle(self.context.title)
        exposure.notifyWorkflowCreated()
        exposure.reindexObject()

        # so redirection via self.getURL will work.
        self.ctxobj = exposure

        if 'export_uri' in self._data and self._data['export_uri']:
            # XXX trap only the right exceptions.
            self.prepareWizard(self._data['export_uri'])

    def prepareWizard(self, uri):
        """\
        Import this structure into the exposure wizard.
        """
        u = urlopen(uri)
        exported = json.load(u)
        u.close()

        wizard = zope.component.getAdapter(self.ctxobj, IExposureWizard)
        wizard.structure = exported

    def render(self):
        if not self._gotExposureContainer:
            # we didn't finish.
            self._finishedAdd = False
        return super(CreateExposureForm, self).render()

    def __call__(self, *a, **kw):
        if not self.traverse_subpath:
            raise NotFound(self.context, self.context.title_or_id())

        try:
            storage = zope.component.getAdapter(self.context, IStorage)
            commit_id = unicode(self.traverse_subpath[0])
            # Make sure this is a valid revision.
            storage.checkout(commit_id)
        except (PathInvalidError, RevisionNotFoundError,):
            raise NotFound(self.context, commit_id)

        return super(CreateExposureForm, self).__call__(*a, **kw)

CreateExposureFormView = layout.wrap_form(CreateExposureForm,
    __wrapper_class=TraverseFormWrapper,
    label="Select 'Add' to begin creating the exposure")


class CreateExposureFormExtender(extensible.FormExtender):
    zope.component.adapts(
        IWorkspace, IBrowserRequest, CreateExposureForm)

    def update(self):
        self.add(IExposureExportImportGroup)
