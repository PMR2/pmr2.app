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
from pmr2.app.exposure.browser.browser import ExposureFileTypeAnnotatorForm
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile

from pmr2.app.exposure.browser.workspace import *

class DummyObject(object):
    pass


class BaseWizardGroup(form.Form, form.Group):
    """\
    Subgroups for the wizard.

    This is a mixin.
    """

    zope.interface.implements(ICurrentCommitIdProvider)

    ignoreContext = False
    structure = None

    def current_commit_id(self):
        return self.context.commit_id

    def getContent(self):
        # assigned by constructor.
        obj = self.dummy()
        for k, v in self.structure.iteritems():
            setattr(obj, k, v)
        if self.field_iface:
            zope.interface.alsoProvides(obj, self.field_iface)
        return obj

    @z3c.form.button.buttonAndHandler(_('Update'), name='update')
    def handleUpdate(self, action):
        """\
        Call update and update the structure we have.
        """

        structure = self.generateStructure()
        self.structure.update(structure)


def mixin_wizard(groupform, object_cls=DummyObject):
    class WizardGroupMixed(BaseWizardGroup, groupform):
        dummy = object_cls
        pass
    #assert IDocGenSubgroup.implementedBy(groupform)
    return WizardGroupMixed

ExposureViewGenWizard = mixin_wizard(ExposureViewGenGroup)
ExposureFileChoiceTypeWizard = mixin_wizard(ExposureFileChoiceTypeGroup)


class ExposureFileTypeAnnotatorSubForm(ExposureFileTypeAnnotatorForm):
    zope.interface.implements(z3c.form.interfaces.ISubForm)
    fields = z3c.form.field.Fields(IExposureFileGenForm)
    prefix = 'annotate'

    ignoreContext = True


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

        self.viewGroup = ExposureViewGenWizard(
            self.context, self.request, self)
        # XXX
        self.viewGroup.structure = {}
        wh = zope.component.getAdapter(self.context, 
            IExposureWizard)
        # XXX placeholder assumption
        if wh.structure:
            self.viewGroup.structure = wh.structure[-1][1]
        self.viewGroup.update()
        self.groups.append(self.viewGroup)

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

