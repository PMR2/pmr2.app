import json

import zope.interface
import zope.component
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

import z3c.form

from plone.z3cform import layout
from plone.z3cform.fieldsets import group, extensible

from pmr2.app.browser import form
from pmr2.app.browser import page
from pmr2.app.browser import widget
from pmr2.app.browser.layout import *

from pmr2.app.workspace.interfaces import ICurrentCommitIdProvider

from pmr2.app.exposure.interfaces import IExposure
from pmr2.app.exposure.browser.interfaces import IExposureExportImportGroup
from pmr2.app.exposure.browser.interfaces import IExposureFileGenForm
from pmr2.app.exposure.browser.interfaces import IExposureWizardForm
from pmr2.app.exposure.browser.browser import BaseExposureFileTypeAnnotatorForm
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile

from pmr2.app.exposure.browser.workspace import *


def _changeWizard(exposure):
    wh = zope.component.getAdapter(exposure, IExposureWizard)
    structure = []
    structure.extend(wh.structure)
    wh.structure = structure


class DummyObject(object):
    pass


class BaseWizardGroup(form.Form, form.Group):
    """\
    Subgroups for the wizard.

    This is a mixin.
    """

    ignoreContext = False
    structure = None

    def getContent(self):
        # assigned by constructor.
        obj = self.dummy()
        for k, v in self.structure.iteritems():
            setattr(obj, k, v)
        if hasattr(self, 'field_iface') and self.field_iface:
            zope.interface.alsoProvides(obj, self.field_iface)
        else:
            # XXX
            self.ignoreContext = True
            zope.interface.alsoProvides(obj, zope.interface.Interface)
        return obj

    @z3c.form.button.buttonAndHandler(_('Update'), name='update')
    def handleUpdate(self, action):
        """\
        Call update and update the structure we have.
        """

        filename, structure = self.generateStructure()
        self.structure.update(structure)

        # trigger the update
        _changeWizard(self.context)


def mixin_wizard(groupform, object_cls=DummyObject):
    class WizardGroupMixed(BaseWizardGroup, groupform):
        dummy = object_cls
        def current_commit_id(self):
            return self.context.commit_id
        def __repr__(self):
            return '<%s for <%s.%s> object at %x' % (
                self.__class__.__name__, 
                groupform.__module__,
                groupform.__name__,
                id(self),
            )

    #assert IDocGenSubgroup.implementedBy(groupform)
    return WizardGroupMixed


class ExposureFileTypeAnnotatorSubForm(BaseExposureFileTypeAnnotatorForm):
    zope.interface.implements(z3c.form.interfaces.ISubForm)
    #fields = z3c.form.field.Fields(IExposureFileGenForm)
    prefix = 'annotate'  # XXX need to be a property based on file.

    ignoreContext = True


ExposureViewGenWizard = mixin_wizard(ExposureViewGenGroup)
ExposureFileChoiceTypeWizard = mixin_wizard(ExposureFileChoiceTypeGroup)
ExposureFileTypeAnnotatorWizard = \
    mixin_wizard(ExposureFileTypeAnnotatorSubForm)


class ExposureWizardForm(form.PostForm, extensible.ExtensibleForm):
    """\
    The exposure wizard.
    """

    zope.interface.implements(IExposureWizardForm)

    ignoreContext = True
    enable_form_tabbing = False

    def __init__(self, *a, **kw):
        super(ExposureWizardForm, self).__init__(*a, **kw)
        self.fields = z3c.form.field.Fields()

    def update(self):
        form.PostForm.update(self)
        self.updateGroups()
        extensible.ExtensibleForm.update(self)

    def updateGroups(self):
        self.groups = []

        wh = zope.component.getAdapter(self.context, 
            IExposureWizard)

        # XXX hack of sort to add the view group to the beginning.
        self.viewGroup = ExposureViewGenWizard(
            self.context, self.request, self)
        self.viewGroup.structure = {}
        if wh.structure:
            self.viewGroup.structure = wh.structure[-1][1]
        self.viewGroup.update()
        self.groups.append(self.viewGroup)

        # handle the rest.
        if not wh.structure:
            return
        structures = wh.structure[:-1]

        for i, o in enumerate(structures):
            grp = ExposureFileTypeAnnotatorWizard(
                self.context, self.request, self)
            filename, structure = o
            grp.structure = structure
            grp.prefix = grp.prefix + str(i)
            self.groups.append(grp)

        # XXX need to expand this.
        #self.fileGroup = ExposureFileChoiceTypeGroup(
            #self.context, self.request, self)
        #self.groups.append(self.fileGroup)

    @z3c.form.button.buttonAndHandler(_('Build'), name='build')
    def handleBuild(self, action):
        """\
        Build the thing
        """

    @z3c.form.button.buttonAndHandler(_('Add File'), name='add_file')
    def handleAddFile(self, action):
        """\
        Add a file
        """

    # subform removes file.

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        """\
        Cancel, revert the states to what is in the structure.
        """

    def render(self):
        return super(ExposureWizardForm, self).render()


class ExposureFileTypeAnnotatorSubFormExtender(extensible.FormExtender):
    # For subform
    # XXX refactor and merge this with the standard form

    zope.component.adapts(
        IExposure, IBrowserRequest, ExposureFileTypeAnnotatorSubForm)

    @property
    def viewsEnabled(self):
        # return a list of views that are enabled.
        return [k for k, v in self.form.structure['views']]

    def update(self):
        # XXX files not included.
        for name in self.viewsEnabled:
            # XXX self.context.views should be a tuple of ascii values
            # taken from the constraint vocabulary of installed views.
            name = name.encode('ascii', 'replace')
            annotatorFactory = zope.component.queryUtility(
                IExposureFileAnnotator, name=name)
            if not annotatorFactory:
                # silently ignore missing fields.
                continue

            annotator = annotatorFactory(self.context, self.request)
            self.add(annotator)

    def add(self, annotator):
        fields = self.makeField(annotator)
        # XXX name may need to reference the path to the file
        name = str(annotator.__name__)
        context = self.context
        ignoreContext = True

        # since the adapter results in a factory that instantiates
        # the annotation, this side effect must be avoided.
        # XXX acquire the saved bits from the structure
        #if has_note(context, name):
        #    ignoreContext = False
        #    context = zope.component.getAdapter(
        #        context, annotator.for_interface, name=name)

        # make the group and assign data.
        g = form.Group(context, self.request, self.form)
        g.__name__ = annotator.title
        g.label = annotator.title
        g.fields = fields
        # XXX ignore it for now since we don't have the temporary one
        g.ignoreContext = True # ignoreContext
        if not fields.keys():
            g.description = u''\
                'There are no editable attributes for this note as values ' \
                'for this annotation are automatically generated.'

        # finally append this group
        self.form.groups.append(g)

    def makeField(self, annotator):
        # this method could potentially be refactored out into an 
        # adapter.
        name = str(annotator.__name__)
        if IExposureFileEditAnnotator.providedBy(annotator) or \
                IExposureFilePostEditAnnotator.providedBy(annotator):
            # edited fields
            fields = z3c.form.field.Fields(annotator.for_interface, 
                                           prefix=name)
            if IExposureFilePostEditAnnotator.providedBy(annotator):
                # select just the fields that will be edited.
                sel = ['%s.%s' % (name, n) for n in annotator.edited_names]
                fields = fields.select(*sel)
        else:
            # no edited fields available.
            fields = z3c.form.field.Fields(prefix=name)
        return fields

