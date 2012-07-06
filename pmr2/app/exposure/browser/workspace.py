import json

import zope.component
import zope.interface
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest

import z3c.form
from plone.z3cform import layout
from plone.z3cform.fieldsets import group, extensible

from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage

from pmr2.app.workspace.interfaces import IStorage, IWorkspace
from pmr2.app.workspace.interfaces import ICurrentCommitIdProvider
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

    zope.interface.implements(ICreateExposureForm)

    label = u"Exposure Creation Wizard"
    description = u"Please fill out the options of only one for the " \
                   "following sets of fields below to begin the exposure " \
                   "creation process."
    _gotExposureContainer = False

    def createAndAdd(self, data):
        obj = super(CreateExposureForm, self).createAndAdd(self)
        self.processGroups()
        return obj

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

    def processGroups(self):
        """\
        Process groups that are here.
        """

        for g in self.groups:
            structure = g.populateExposure(self.ctxobj)
            wh = zope.component.getAdapter(self.ctxobj, 
                IExposureWizard)
            if structure:
                wh.structure = structure
                break

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


class CreateExposureGroupBase(form.Group):
    """\
    Base group for extending the exposure creator.
    """

    zope.interface.implements(ICreateExposureGroup)

    ignoreContext = True
    order = 0

    def populateExposure(self, exposure):
        """\
        """

        raise NotImplementedError


class DocGenSubgroup(form.Group):
    """\
    Subgroup for docgen.
    """

    zope.interface.implements(ICurrentCommitIdProvider)
    ignoreContext = True

    def current_commit_id(self):
        # XXX this is a hack, should use some sort of adapter.
        return self.parentForm.parentForm.traverse_subpath[0]


class ExposureViewGenGroup(DocGenSubgroup):
    """\
    Subgroup for the main exposure view generator.
    """

    label = 'Exposure main view'
    fields = z3c.form.field.Fields(IExposureViewGenGroup)


class ExposureFileChoiceTypeGroup(DocGenSubgroup):
    """\
    Subgroup for the main exposure view generator.
    """

    label = 'Add model file'
    fields = z3c.form.field.Fields(IExposureFileChoiceTypeGroup)


class DocGenGroup(CreateExposureGroupBase):
    """\
    Group for the document generation.
    """

    label = "Standard exposure creator"
    description = "Please select the base file and/or the generation method."
    prefix = 'docgen'
    order = -10

    def update(self):
        # XXX once the following are properly for the wizard, maybe we
        # reuse the ones there.
        # XXX also turn these into adapters, but they need to implement
        # the handelers.
        self.groups = []
        self.groups.append(ExposureViewGenGroup(
            self.context, self.request, self))
        self.groups.append(ExposureFileChoiceTypeGroup(
            self.context, self.request, self))

        return super(DocGenGroup, self).update()

    def populateExposure(self, exposure):
        data, errors = self.extractData()
        if errors:
            return

        if not data['generator'] and not data['filename']:
            # no root document and no filename to the first file.
            return

        first_file = (data['filename'], {
            'file_type': data['filetype'],
            'views': [],
            'selected_view': None,
            'Subject': (),
        })

        root = ('', {
            # XXX again, assuming parentForm (see above hack).
            'commit_id': self.parentForm.traverse_subpath[0],
            'curation': {},  # XXX no interface yet
            'docview_generator': data['generator'],
            'docview_gensource': data['source'],
            'title': u'',  # XXX copy context?
            'workspace': u'/'.join(self.context.getPhysicalPath()),
            'Subject': (),  # XXX to be assigned by filetype?
        })

        if data['filename']:
            structure = [first_file, root]
        else:
            structure = [root]

        return structure


class ExposureImportExportGroup(CreateExposureGroupBase):
    """\
    Group for the document generation.
    """

    fields = z3c.form.field.Fields(IExposureExportImportGroup)
    label = "Exposure Import via URI"
    prefix = 'exportimport'

    def populateExposure(self, exposure):
        data, errors = self.extractData()
        uri = data.get('export_uri', None)

        if uri:
            # XXX no exception handling here.
            u = urlopen(uri)
            exported = json.load(u)
            u.close()
            return exported


class CreateExposureFormExtender(extensible.FormExtender):
    zope.component.adapts(
        IWorkspace, IBrowserRequest, ICreateExposureForm)

    def update(self):
        # Collect all the groups, instantiate them, add them to parent.
        groups = zope.component.getAdapters(
            (self.context, self.request, self.form),
            ICreateExposureGroup,
        )
        for k, g in sorted(groups, key=extensible.order_key):
            self.add(g)

    def add(self, group):
        self.form.groups.append(group)

